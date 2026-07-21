from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
from huggingface_hub import hf_hub_download
import os

# Find downloaded weights path
weights_path = hf_hub_download(repo_id="dronefreak/visdrone-yolov8x", filename="best.pt")
model = YOLO(weights_path)

OUTPUT_DIR = Path("/home/vasile/.gemini/antigravity/brain/923beaef-e863-4f20-b1bf-32bb66d46226/detections")
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMAGES = [
    Path("street_cleanup/renders/511/30436272704361607511.jpg"),
    Path("street_cleanup/renders/513/30436272704361607513.jpg"),
    Path("street_cleanup/renders/515/30436272704361607515.jpg"),
    Path("street_cleanup/renders/517/30436272704361607517.jpg"),
    Path("street_cleanup/renders/531/30436272704361607531.jpg")
]

# VisDrone vehicle classes: 3 (car), 4 (van), 5 (truck), 8 (bus)
VEHICLE_CLASSES = [3, 4, 5, 8]

def main():
    print(f"Loaded YOLOv8 VisDrone model from: {weights_path}")
    print(f"Model classes: {model.names}")
    
    for img_path in IMAGES:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
            
        results = model.predict(img, conf=0.15, classes=VEHICLE_CLASSES, verbose=False)
        boxes = results[0].boxes
        print(f"File {img_path.name}: detected {len(boxes)} vehicles")
        
        annotated = img.copy()
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls_id]
            tx1, ty1, tx2, ty2 = box.xyxy[0].tolist()
            cv2.rectangle(annotated, (int(tx1), int(ty1)), (int(tx2), int(ty2)), (255, 0, 0), 2)
            cv2.putText(annotated, f"{name} {conf:.2f}", (int(tx1), int(ty1)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            
        out_path = OUTPUT_DIR / f"{img_path.stem}_visdrone.jpg"
        cv2.imwrite(str(out_path), annotated)
        print(f"Saved annotated image to {out_path}")

if __name__ == "__main__":
    main()
