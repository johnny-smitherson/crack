# Street Cleanup Pipeline Results Summary

This document summarizes the results of the street obstacle detection and mesh flattening pipeline run.

## Key Statistics

- **Total Obstacles Detected and Projected**: 1
- **Unique Map Tiles Affected**: 1
- **Average Detection Distance**: 1.66 meters

## Detections Breakdown

| Class | Count | Description |
|---|---|---|
| **car** | 1 | Satellite-captured parked/moving cars on streets and sidewalks |

## Technical Implementation Details

1. **OSM Street Extraction**: Buffered OSM road centerlines with an extra 1.5-meter sidewalk padding to identify street areas.
2. **Perspective Viewport Rendering**: Placed cameras at street level (1.8m height) using target headings along road paths, avoiding top-down projection distortions.
3. **YOLO Detection & Raycast**: Used YOLOv11m to locate obstacles and Blender `scene.ray_cast` to project pixel centers back to exact 3D coordinates.
4. **Mesh Flattening**: Replaced height coordinates of affected vertices in-place with the median height of local boundary rings to preserve slope profiles.
