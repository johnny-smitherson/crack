import cv2
import numpy as np

img = cv2.imread("street_cleanup/renders/511/30436272704361607511.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Search Hue range
for h_min in range(0, 180, 10):
    h_max = h_min + 10
    mask = cv2.inRange(hsv, np.array([h_min, 20, 20]), np.array([h_max, 255, 255]))
    count = np.sum(mask > 0)
    if count > 0:
        print(f"Hue {h_min}-{h_max}: {count} pixels")
