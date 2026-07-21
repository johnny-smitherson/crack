from ultralytics import YOLO
import cv2
import numpy as np

IMAGE_PATH = "street_cleanup/renders/511/30436272704361607511.jpg"

def main():
    print("Loading YOLOv8 VisDrone...")
    # This will download the model automatically from Hugging Face if needed
    model = YOLO("mshamrai/yolov8x-visdrone")
    
    results = model.predict(IMAGE_PATH, conf=0.15, verbose=False)
    print(f"YOLOv8 VisDrone detected {len(results[0].boxes)} objects:")
    
    img = cv2.imread(IMAGE_PATH)
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        name = model.names[cls_id]
        print(f"  Class {cls_id} ({name}): {conf:.4f}")
        
        tx1, ty1, tx2, ty2 = box.xyxy[0].tolist()
        cv2.rectangle(img, (int(tx1), int(ty1)), (int(tx2), int(ty2)), (255, 0, 0), 2)
        cv2.putText(img, f"{name}", (int(tx1), int(ty1)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
    cv2.imwrite("street_cleanup/visdrone_test.jpg", img)
    print("Saved VisDrone test image to street_cleanup/visdrone_test.jpg")

if __name__ == "__main__":
    main()
