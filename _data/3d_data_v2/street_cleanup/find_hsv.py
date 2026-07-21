import cv2
import numpy as np

img = cv2.imread("street_cleanup/renders/511/30436272704361607511.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

h, w, _ = img.shape
green_pixels = []

for y in range(h):
    for x in range(w):
        b, g, r = img[y, x]
        # If green channel is significantly larger than blue and red
        if int(g) > int(b) + 10 and int(g) > int(r) + 10:
            green_pixels.append(hsv[y, x])

if green_pixels:
    green_pixels = np.array(green_pixels)
    print(f"Found {len(green_pixels)} green-ish pixels.")
    print(f"Min HSV: {green_pixels.min(axis=0)}")
    print(f"Max HSV: {green_pixels.max(axis=0)}")
    print(f"Mean HSV: {green_pixels.mean(axis=0)}")
else:
    print("No green-ish pixels found with G > B+10 and G > R+10")
