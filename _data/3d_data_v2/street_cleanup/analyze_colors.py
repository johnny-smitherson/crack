import cv2
import numpy as np

img = cv2.imread("street_cleanup/renders/511/30436272704361607511.jpg")
if img is not None:
    # Print average RGB
    mean_color = cv2.mean(img)[:3]
    print(f"Mean BGR: {mean_color}")
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print(f"Mean HSV: {cv2.mean(hsv)[:3]}")
    # Print max and min values
    print(f"Min HSV: {hsv.min(axis=(0,1))}")
    print(f"Max HSV: {hsv.max(axis=(0,1))}")
else:
    print("Failed to load image")
