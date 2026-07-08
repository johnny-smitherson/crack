"""
Satellite Car Detection Exploration Script
Runs sliding-window tiled detection using:
- YOLO11x (COCO baseline)
- YOLOv8x-VisDrone (aerial fine-tuned)
- YOLOv7-m ITCVD ONNX (satellite/aerial specific)
Then applies Non-Maximum Suppression (NMS) to merge overlapping detections and saves annotated outputs.
"""

from __future__ import annotations

import time
import logging
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("satellite_detect")

# Paths
SANDBOX_DIR = Path(__file__).parent.resolve()
IMAGE_PATH = SANDBOX_DIR / "demo1.jpg"
YOLOV7_ONNX_PATH = SANDBOX_DIR / "yolov7-m_itcvd_qgis.onnx"
YOLOV8_VISDRONE_PATH = SANDBOX_DIR / "yolov8x_visdrone.pt"

# Configuration
TILE_SIZE = 640
OVERLAP = 128
CONF_THRESHOLD = 0.25
NMS_IOU_THRESHOLD = 0.4

def tile_image(image: np.ndarray, tile_size: int = 640, overlap: int = 128) -> list[tuple[int, int, np.ndarray]]:
    """Splits image into overlapping tiles. Returns list of (x_offset, y_offset, tile_img)."""
    h, w, _ = image.shape
    tiles = []
    
    y_starts = list(range(0, h - tile_size, tile_size - overlap))
    if not y_starts or y_starts[-1] + tile_size < h:
        y_starts.append(h - tile_size)
        
    x_starts = list(range(0, w - tile_size, tile_size - overlap))
    if not x_starts or x_starts[-1] + tile_size < w:
        x_starts.append(w - tile_size)
        
    for y in y_starts:
        for x in x_starts:
            tiles.append((x, y, image[y:y+tile_size, x:x+tile_size]))
            
    return tiles

def apply_nms(detections: list[dict], iou_threshold: float = 0.4) -> list[dict]:
    """Applies Non-Maximum Suppression to filter overlapping detections."""
    if not detections:
        return []
    
    # Format boxes for cv2 NMS: [x, y, w, h]
    boxes = []
    scores = []
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        boxes.append([x1, y1, x2 - x1, y2 - y1])
        scores.append(det["confidence"])
        
    indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.01, nms_threshold=iou_threshold)
    
    # Flatten indices if needed (depends on cv2 version, sometimes it's 2D array or 1D list)
    if len(indices) > 0:
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()
        elif isinstance(indices[0], (list, tuple, np.ndarray)):
            indices = [idx[0] for idx in indices]
        return [detections[idx] for idx in indices]
    return []

def run_yolov7_onnx(image: np.ndarray, net: cv2.dnn.Net, tile_size: int = 640, overlap: int = 128) -> list[dict]:
    """Runs YOLOv7 ONNX model on the image using sliding window tiling."""
    tiles = tile_image(image, tile_size, overlap)
    raw_detections = []
    
    for x_offset, y_offset, tile_img in tiles:
        # Preprocess
        blob = cv2.dnn.blobFromImage(tile_img, 1.0 / 255.0, (tile_size, tile_size), (0, 0, 0), swapRB=True, crop=False)
        net.setInput(blob)
        outputs = net.forward() # shape: (1, 25200, 6)
        
        predictions = outputs[0]
        for pred in predictions:
            # pred: [x_center, y_center, w, h, objectness, class_prob]
            obj_conf = pred[4]
            class_prob = pred[5]
            confidence = obj_conf * class_prob
            
            if confidence >= CONF_THRESHOLD:
                x_c, y_c, w, h = pred[0:4]
                
                # Convert to absolute pixel coordinates on the full image
                x1 = int((x_c - w / 2) + x_offset)
                y1 = int((y_c - h / 2) + y_offset)
                x2 = int((x_c + w / 2) + x_offset)
                y2 = int((y_c + h / 2) + y_offset)
                
                raw_detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(confidence),
                    "class_name": "car",
                    "class_id": 0
                })
                
    return apply_nms(raw_detections, NMS_IOU_THRESHOLD)

def run_ultralytics_yolo(image: np.ndarray, model: YOLO, target_classes: list[int] | None = None, tile_size: int = 640, overlap: int = 128) -> list[dict]:
    """Runs an Ultralytics YOLO model on the image using sliding window tiling."""
    tiles = tile_image(image, tile_size, overlap)
    raw_detections = []
    
    # Process tile by tile
    for x_offset, y_offset, tile_img in tiles:
        # Run inference
        results = model.predict(tile_img, conf=CONF_THRESHOLD, imgsz=tile_size, verbose=False)
        
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            if target_classes is not None and cls_id not in target_classes:
                continue
                
            conf = float(box.conf[0])
            # Bounding box in tile-local pixel space [x1, y1, x2, y2]
            tx1, ty1, tx2, ty2 = box.xyxy[0].tolist()
            
            # Map back to full image coordinate space
            x1 = int(tx1 + x_offset)
            y1 = int(ty1 + y_offset)
            x2 = int(tx2 + x_offset)
            y2 = int(ty2 + y_offset)
            
            raw_detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "class_name": model.names[cls_id],
                "class_id": cls_id
            })
            
    return apply_nms(raw_detections, NMS_IOU_THRESHOLD)

def draw_and_save(image: np.ndarray, detections: list[dict], output_path: Path, title: str):
    """Draws detections on the image and saves it."""
    annotated = image.copy()
    h, w, _ = annotated.shape
    
    # Choose color based on model
    if "visdrone" in title.lower():
        color = (255, 0, 0) # Blue
    elif "yolov7" in title.lower():
        color = (0, 0, 255) # Red
    else:
        color = (0, 255, 0) # Green
        
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        # Clip bounding box coordinates to image dimensions
        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(0, min(w - 1, x2))
        y2 = max(0, min(h - 1, y2))
        
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        label = f"{det['class_name']}: {det['confidence']:.2f}"
        cv2.putText(
            annotated,
            label,
            (x1, max(y1 - 5, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            color,
            1,
            cv2.LINE_AA
        )
        
    cv2.putText(
        annotated,
        f"{title} - Total detections: {len(detections)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        color,
        2,
        cv2.LINE_AA
    )
    
    cv2.imwrite(str(output_path), annotated)
    logger.info("Saved annotated image to %s", output_path)

def main():
    logger.info("Starting satellite detection exploration")
    
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Source image not found: {IMAGE_PATH}")
        
    img = cv2.imread(str(IMAGE_PATH))
    if img is None:
        raise ValueError(f"Failed to load image: {IMAGE_PATH}")
        
    logger.info("Loaded source image: %s (Dimensions: %s)", IMAGE_PATH.name, img.shape)
    
    # 1. Evaluate YOLO11x (COCO baseline)
    logger.info("--- 1. Running YOLO11x (COCO Baseline) ---")
    try:
        t0 = time.time()
        yolo11 = YOLO("yolo11x.pt")
        # COCO classes for vehicles: 2 (car), 3 (motorcycle), 5 (bus), 7 (truck)
        coco_vehicles = [2, 3, 5, 7]
        detections_y11 = run_ultralytics_yolo(img, yolo11, target_classes=coco_vehicles)
        t_y11 = time.time() - t0
        logger.info("YOLO11x finished in %.2f seconds. Detected: %d vehicles.", t_y11, len(detections_y11))
        draw_and_save(img, detections_y11, SANDBOX_DIR / "yolo11x_detections.jpg", "YOLO11x COCO")
    except Exception as e:
        logger.exception("Failed to run YOLO11x: %s", e)
        detections_y11 = []
        t_y11 = 0
        
    # 2. Evaluate YOLOv8x-VisDrone
    logger.info("--- 2. Running YOLOv8x-VisDrone ---")
    try:
        t0 = time.time()
        yolov8_vd = YOLO(str(YOLOV8_VISDRONE_PATH))
        # VisDrone classes for vehicles: 3 (car), 4 (van), 5 (truck), 8 (bus)
        visdrone_vehicles = [3, 4, 5, 8]
        detections_v8_vd = run_ultralytics_yolo(img, yolov8_vd, target_classes=visdrone_vehicles)
        t_v8_vd = time.time() - t0
        logger.info("YOLOv8x-VisDrone finished in %.2f seconds. Detected: %d vehicles.", t_v8_vd, len(detections_v8_vd))
        draw_and_save(img, detections_v8_vd, SANDBOX_DIR / "yolov8x_visdrone_detections.jpg", "YOLOv8x VisDrone")
    except Exception as e:
        logger.exception("Failed to run YOLOv8x-VisDrone: %s", e)
        detections_v8_vd = []
        t_v8_vd = 0

    # 3. Evaluate YOLOv7-m ITCVD ONNX
    logger.info("--- 3. Running YOLOv7-m ITCVD ONNX ---")
    try:
        t0 = time.time()
        net = cv2.dnn.readNetFromONNX(str(YOLOV7_ONNX_PATH))
        detections_y7 = run_yolov7_onnx(img, net)
        t_y7 = time.time() - t0
        logger.info("YOLOv7-m ITCVD ONNX finished in %.2f seconds. Detected: %d vehicles.", t_y7, len(detections_y7))
        draw_and_save(img, detections_y7, SANDBOX_DIR / "yolov7_itcvd_detections.jpg", "YOLOv7 ITCVD ONNX")
    except Exception as e:
        logger.exception("Failed to run YOLOv7-m ITCVD: %s", e)
        detections_y7 = []
        t_y7 = 0

    # Comparison summary report
    print("\n" + "=" * 60)
    print("DETECTION COMPARISON SUMMARY")
    print("=" * 60)
    print(f"1. YOLO11x (COCO Baseline)    : {len(detections_y11)} detections, Time: {t_y11:.2f}s")
    print(f"2. YOLOv8x-VisDrone           : {len(detections_v8_vd)} detections, Time: {t_v8_vd:.2f}s")
    print(f"3. YOLOv7-m ITCVD (ONNX)       : {len(detections_y7)} detections, Time: {t_y7:.2f}s")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
