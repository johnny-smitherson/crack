import cv2
import numpy as np
from pathlib import Path
import os

YOLOV7_ONNX_PATH = Path("/home/vasile/.gemini/antigravity/scratch/crack/_slop/detection_sandbox/yolov7-m_itcvd_qgis.onnx")
OUTPUT_DIR = Path("/home/vasile/.gemini/antigravity/brain/923beaef-e863-4f20-b1bf-32bb66d46226/detections")
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMAGES = [
    Path("street_cleanup/renders/511/30436272704361607511.jpg"),
    Path("street_cleanup/renders/513/30436272704361607513.jpg"),
    Path("street_cleanup/renders/515/30436272704361607515.jpg"),
    Path("street_cleanup/renders/517/30436272704361607517.jpg"),
    Path("street_cleanup/renders/531/30436272704361607531.jpg")
]

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

def main():
    print("Loading YOLOv7 ONNX net...")
    net = cv2.dnn.readNetFromONNX(str(YOLOV7_ONNX_PATH))
    
    for img_path in IMAGES:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Skipping {img_path} - not found")
            continue
            
        dets = run_yolov7_onnx(img, net, conf_threshold=0.20)
        print(f"File {img_path.name}: detected {len(dets)} cars")
        
        annotated = img.copy()
        for d in dets:
            x1, y1, x2, y2 = d["bbox"]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(annotated, f"car {d['confidence']:.2f}", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            
        out_path = OUTPUT_DIR / f"{img_path.stem}_yolov7.jpg"
        cv2.imwrite(str(out_path), annotated)
        print(f"Saved annotated image to {out_path}")

if __name__ == "__main__":
    main()
