import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import sys

# Paths
IMAGE_PATH = Path("street_cleanup/renders/511/30436272704361607511.jpg")
YOLOV7_ONNX_PATH = Path("/home/vasile/.gemini/antigravity/scratch/crack/_slop/detection_sandbox/yolov7-m_itcvd_qgis.onnx")

def run_yolov7_onnx(image: np.ndarray, net, conf_threshold=0.25) -> list[dict]:
    h_img, w_img, _ = image.shape
    blob = cv2.dnn.blobFromImage(image, 1.0 / 255.0, (640, 640), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward()
    predictions = outputs[0]
    raw_detections = []
    for pred in predictions:
        obj_conf = pred[4]
        class_prob = pred[5]
        confidence = obj_conf * class_prob
        if confidence >= conf_threshold:
            x_c, y_c, w, h = pred[0:4]
            x_c = (x_c / 640.0) * w_img
            y_c = (y_c / 640.0) * h_img
            w = (w / 640.0) * w_img
            h = (h / 640.0) * h_img
            x1 = int(x_c - w / 2)
            y1 = int(y_c - h / 2)
            x2 = int(x_c + w / 2)
            y2 = int(y_c + h / 2)
            raw_detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": float(confidence),
                "class_name": "car"
            })
    # NMS
    boxes = [[d["bbox"][0], d["bbox"][1], d["bbox"][2]-d["bbox"][0], d["bbox"][3]-d["bbox"][1]] for d in raw_detections]
    scores = [d["confidence"] for d in raw_detections]
    indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.01, nms_threshold=0.4)
    if len(indices) > 0:
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()
        return [raw_detections[idx] for idx in indices]
    return []

def tile_image(image: np.ndarray, tile_size=640, overlap=128):
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

def apply_nms(detections, iou_threshold=0.4):
    if not detections:
        return []
    boxes = [[d["bbox"][0], d["bbox"][1], d["bbox"][2]-d["bbox"][0], d["bbox"][3]-d["bbox"][1]] for d in detections]
    scores = [d["confidence"] for d in detections]
    indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.01, nms_threshold=iou_threshold)
    if len(indices) > 0:
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()
        return [detections[idx] for idx in indices]
    return []

def run_yolo11_tiled(image: np.ndarray, model, conf_threshold=0.15) -> list[dict]:
    tiles = tile_image(image, tile_size=640, overlap=128)
    raw_detections = []
    for x_offset, y_offset, tile_img in tiles:
        results = model.predict(tile_img, conf=conf_threshold, imgsz=640, verbose=False)
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            tx1, ty1, tx2, ty2 = box.xyxy[0].tolist()
            x1 = int(tx1 + x_offset)
            y1 = int(ty1 + y_offset)
            x2 = int(tx2 + x_offset)
            y2 = int(ty2 + y_offset)
            raw_detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "class_id": cls_id,
                "class_name": model.names[cls_id]
            })
    return apply_nms(raw_detections)

def main():
    img = cv2.imread(str(IMAGE_PATH))
    if img is None:
        print(f"Error loading image: {IMAGE_PATH}")
        sys.exit(1)
        
    print("Running YOLOv7 ONNX...")
    net = cv2.dnn.readNetFromONNX(str(YOLOV7_ONNX_PATH))
    dets_y7 = run_yolov7_onnx(img, net)
    print(f"YOLOv7 ONNX detected {len(dets_y7)} cars.")
    
    # Save YOLOv7 output
    img_y7 = img.copy()
    for d in dets_y7:
        x1, y1, x2, y2 = d["bbox"]
        cv2.rectangle(img_y7, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.imwrite("street_cleanup/yolov7_test.jpg", img_y7)
    
    print("Running YOLOv11 COCO directly...")
    model = YOLO("yolo11x.pt")
    results = model.predict(str(IMAGE_PATH), conf=0.25, verbose=False)
    print(f"YOLOv11 direct detected {len(results[0].boxes)} objects.")
    
    # Save YOLOv11 direct output
    img_y11 = img.copy()
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        tx1, ty1, tx2, ty2 = box.xyxy[0].tolist()
        cv2.rectangle(img_y11, (int(tx1), int(ty1)), (int(tx2), int(ty2)), (0, 255, 0), 2)
    cv2.imwrite("street_cleanup/yolo11_direct_test.jpg", img_y11)
    
    print("Running YOLOv11 COCO tiled...")
    dets_tiled = run_yolo11_tiled(img, model, conf_threshold=0.15)
    print(f"YOLOv11 tiled detected {len(dets_tiled)} objects.")
    
    # Save YOLOv11 tiled output
    img_tiled = img.copy()
    for d in dets_tiled:
        x1, y1, x2, y2 = d["bbox"]
        color = (0, 255, 0) if d["class_name"] == "potted plant" or d["class_id"] == 58 else (255, 0, 0)
        cv2.rectangle(img_tiled, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img_tiled, f"{d['class_name']}", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    cv2.imwrite("street_cleanup/yolo11_tiled_test.jpg", img_tiled)

if __name__ == "__main__":
    main()
