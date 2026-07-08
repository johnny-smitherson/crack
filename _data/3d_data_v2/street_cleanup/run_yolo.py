"""
Run YOLO object detection on rendered street-level images.

Loads the rendered JPEGs, runs YOLO inference to detect vehicles (cars, trucks,
buses, motorcycles), and saves the 2D bounding boxes + camera metadata to a JSON
file for 3D back-projection.

Output:
  - street_cleanup/yolo_detections_2d.json

Run from _data/3d_data_v2/:
    uv run python street_cleanup/run_yolo.py
"""

import json
import logging
import os
import sys
from pathlib import Path
from ultralytics import YOLO

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("run_yolo")

RENDERS_DIR = Path("street_cleanup/renders")
OUTPUT_PATH = Path("street_cleanup/yolo_detections_2d.json")

# COCO vehicle classes: 2=car, 3=motorcycle, 5=bus, 7=truck
# COCO potted plant (58) as a proxy for small trees/bushes
TARGET_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    58: "tree_proxy",
}


def main():
    logger.info("=" * 60)
    logger.info("Running YOLO Vehicle & Obstacle Detection")
    logger.info("=" * 60)

    if not RENDERS_DIR.exists():
        logger.error(f"Renders directory not found: {RENDERS_DIR}")
        sys.exit(1)

    # Find all successfully rendered JPG files that have matching JSON metadata
    jpg_files = []
    for f in RENDERS_DIR.glob("*.jpg"):
        meta_file = f.with_suffix(".json")
        if meta_file.exists() and f.name != "test.jpg":
            jpg_files.append(f)

    logger.info(f"Found {len(jpg_files)} rendered viewpoints to process.")
    if not jpg_files:
        logger.warning("No viewpoints to process. Render some views first!")
        sys.exit(0)

    # Load YOLO model (medium for high accuracy, auto-downloads on first use)
    model_name = "yolo11m.pt"
    logger.info(f"Loading YOLO model: {model_name}...")
    model = YOLO(model_name)

    detections_2d = []

    for i, jpg_path in enumerate(jpg_files, start=1):
        vp_id = int(jpg_path.stem)
        meta_path = jpg_path.with_suffix(".json")
        
        # Load viewpoint metadata
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            
        # Run inference
        results = model.predict(
            source=str(jpg_path),
            conf=0.25,      # confidence threshold
            iou=0.45,       # NMS IoU threshold
            classes=list(TARGET_CLASSES.keys()),
            verbose=False,
        )
        
        # Extract detections
        result = results[0]
        boxes = result.boxes
        
        vp_detections = []
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist() # [x1, y1, x2, y2] in pixels
            
            # Map tree_proxy class to tree
            cls_name = "tree" if cls_id == 58 else TARGET_CLASSES[cls_id]
            
            vp_detections.append({
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": round(conf, 4),
                "bbox_pixel": [round(val, 1) for val in xyxy], # [x1, y1, x2, y2]
            })
            
        if vp_detections:
            detections_2d.append({
                "viewpoint_id": vp_id,
                "glb_path": meta["glb_path"],
                "camera_pos_blender": meta["camera_pos_blender"],
                "matrix_world": meta["matrix_world"],
                "camera_fov": meta["camera_fov"],
                "clip_start": meta["clip_start"],
                "clip_end": meta["clip_end"],
                "detections": vp_detections,
            })
            
        if i % 50 == 0 or i == len(jpg_files):
            logger.info(f"Processed {i}/{len(jpg_files)} viewpoints. Detections found in {len(detections_2d)} viewpoints.")

    # Save to file
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(detections_2d, f, indent=2)

    logger.info(f"Saved 2D detections to {OUTPUT_PATH}")
    
    # Calculate stats
    total_det = sum(len(vp["detections"]) for vp in detections_2d)
    class_counts = {}
    for vp in detections_2d:
        for det in vp["detections"]:
            name = det["class_name"]
            class_counts[name] = class_counts.get(name, 0) + 1
            
    logger.info(f"Total objects detected: {total_det}")
    for name, count in class_counts.items():
        logger.info(f"  {name}: {count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
