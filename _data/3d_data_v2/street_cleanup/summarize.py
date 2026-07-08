"""
Generates a summary report of the street obstacle detection & flattening pipeline.

Reads yolo_detections_3d.json and generates RESULTS.md in the street_cleanup/ folder.

Run from _data/3d_data_v2/:
    uv run python street_cleanup/summarize.py
"""

import json
import os
import sys
from pathlib import Path

INPUT_PATH = Path("street_cleanup/yolo_detections_3d.json")
RESULTS_PATH = Path("street_cleanup/RESULTS.md")


def main():
    if not INPUT_PATH.exists():
        print(f"Error: 3D detections file not found at {INPUT_PATH}")
        sys.exit(1)
        
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        detections = json.load(f)
        
    total_detections = len(detections)
    
    # Calculate class counts
    class_counts = {}
    tiles_affected = set()
    total_dist = 0.0
    
    for d in detections:
        cls_name = d["class_name"]
        class_counts[cls_name] = class_counts.get(cls_name, 0) + 1
        tiles_affected.add(d["glb_path"])
        total_dist += d["distance_meters"]
        
    avg_dist = total_dist / total_detections if total_detections > 0 else 0.0
    
    markdown = f"""# Street Cleanup Pipeline Results Summary

This document summarizes the results of the street obstacle detection and mesh flattening pipeline run.

## Key Statistics

- **Total Obstacles Detected and Projected**: {total_detections}
- **Unique Map Tiles Affected**: {len(tiles_affected)}
- **Average Detection Distance**: {avg_dist:.2f} meters

## Detections Breakdown

| Class | Count | Description |
|---|---|---|
"""
    
    descriptions = {
        "car": "Satellite-captured parked/moving cars on streets and sidewalks",
        "truck": "Delivery trucks, commercial vehicles, and large vans",
        "bus": "Public transit buses and coaches",
        "motorcycle": "Motorcycles, scooters, and mopeds",
        "tree": "Trees and large bushes obstructing roadways/sidewalks",
    }
    
    for name, count in class_counts.items():
        desc = descriptions.get(name, "Other road obstacle")
        markdown += f"| **{name}** | {count} | {desc} |\n"
        
    markdown += """
## Technical Implementation Details

1. **OSM Street Extraction**: Buffered OSM road centerlines with an extra 1.5-meter sidewalk padding to identify street areas.
2. **Perspective Viewport Rendering**: Placed cameras at street level (1.8m height) using target headings along road paths, avoiding top-down projection distortions.
3. **YOLO Detection & Raycast**: Used YOLOv11m to locate obstacles and Blender `scene.ray_cast` to project pixel centers back to exact 3D coordinates.
4. **Mesh Flattening**: Replaced height coordinates of affected vertices in-place with the median height of local boundary rings to preserve slope profiles.
"""
    
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write(markdown)
        
    print(f"Generated summary report at {RESULTS_PATH}")


if __name__ == "__main__":
    main()
