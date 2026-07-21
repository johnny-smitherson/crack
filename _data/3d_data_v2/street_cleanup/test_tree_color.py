import cv2
import numpy as np
from pathlib import Path

IMAGE_PATH = Path("street_cleanup/renders/511/30436272704361607511.jpg")

def main():
    img = cv2.imread(str(IMAGE_PATH))
    if img is None:
        print("Error loading image")
        return
        
    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define range of green color in HSV (Hue is 0-180 in OpenCV)
    # Typical green hue range is 35 to 85.
    lower_green = np.array([35, 30, 30])
    upper_green = np.array([85, 255, 255])
    
    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    annotated = img.copy()
    tree_count = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > 100: # Filter out noise
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(annotated, "tree", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            tree_count += 1
            
    print(f"Detected {tree_count} trees based on green color.")
    cv2.imwrite("street_cleanup/tree_color_test.jpg", annotated)

if __name__ == "__main__":
    main()
