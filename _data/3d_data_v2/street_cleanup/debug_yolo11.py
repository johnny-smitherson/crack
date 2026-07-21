from ultralytics import YOLO
import sys

IMAGE_PATH = "street_cleanup/renders/511/30436272704361607511.jpg"

def main():
    model = YOLO("yolo11x.pt")
    results = model.predict(IMAGE_PATH, conf=0.05, verbose=False)
    print(f"YOLOv11x detected {len(results[0].boxes)} objects with conf >= 0.05:")
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        name = model.names[cls_id]
        print(f"  Class {cls_id} ({name}): {conf:.4f}")

if __name__ == "__main__":
    main()
