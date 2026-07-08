"""
Blender script: Project 2D detections back into 3D world space using raycasting.

Reads yolo_detections_2d.json, loads each GLB tile, constructs camera rays for
each detected object's bounding box center, casts the ray in Blender, and
records the 3D coordinates.

Run via Blender:
    blender -b -P street_cleanup/project_detections.py
"""

import bpy
import sys
import json
import math
import os
from mathutils import Vector, Matrix

# Shift constant to convert Blender coordinates back to True ENU
SHIFT_NORTH = 21392.2

INPUT_PATH = "street_cleanup/yolo_detections_2d.json"
OUTPUT_PATH = "street_cleanup/yolo_detections_3d.json"


def project_ray(px, py, width, height, fov, matrix_world):
    """
    Convert a screen pixel coordinate to a 3D ray origin and direction in world space.
    """
    # 1. Normalized Device Coordinates (NDC) from -1.0 to 1.0
    ndc_x = (px / width) * 2.0 - 1.0
    ndc_y = 1.0 - (py / height) * 2.0
    
    # 2. Camera space ray direction
    # Blender camera looks down -Z in its local space.
    # The focal length in NDC units is 1.0 / tan(fov / 2.0).
    focal_len = 1.0 / math.tan(fov / 2.0)
    ray_cam = Vector((ndc_x, ndc_y, -focal_len)).normalized()
    
    # 3. Transform to world space
    mat = Matrix(matrix_world)
    ray_origin = mat.to_translation()
    # Rotate the camera-space ray to world space
    ray_world = (mat.to_3x3() @ ray_cam).normalized()
    
    return ray_origin, ray_world


def main():
    print("=" * 60)
    print("Blender 3D Back-Projection & Raycasting")
    print("=" * 60)
    
    if not os.path.exists(INPUT_PATH):
        print(f"Error: 2D detections file not found at {INPUT_PATH}")
        sys.exit(1)
        
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        detections_2d = json.load(f)
        
    print(f"Loaded {len(detections_2d)} viewpoints with detections.")
    
    # 1. Collect all unique GLB files in the batch
    glb_paths = set()
    for item in detections_2d:
        glb_paths.add(item["glb_path"])
        
    print(f"Loading {len(glb_paths)} unique GLB tiles into the scene...")
    
    # 2. Clear scene and load all GLBs
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        for glb in glb_paths:
            print(f"  Importing GLB: {glb}")
            bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb))
        bpy.context.view_layer.update()
    except Exception as e:
        print(f"Failed to set up scene: {e}")
        sys.exit(1)
        
    scene = bpy.context.scene
    depsgraph = bpy.context.view_layer.depsgraph
    detections_3d = []
    
    # 3. Perform raycasting for all detections
    for vp in detections_2d:
        vp_id = vp["viewpoint_id"]
        glb_path = vp["glb_path"]
        matrix_world = vp["matrix_world"]
        fov = vp["camera_fov"]
        
        for det in vp["detections"]:
            # Calculate bounding box center in pixels
            x1, y1, x2, y2 = det["bbox_pixel"]
            px = (x1 + x2) / 2.0
            py = (y1 + y2) / 2.0
            
            # Project pixel to 3D ray
            ray_origin, ray_world = project_ray(px, py, 640, 640, fov, matrix_world)
            print(f"DEBUG: ray_origin={ray_origin}, ray_world={ray_world}")
            
            # Perform raycast in Blender
            hit, location, normal, index, obj, matrix = scene.ray_cast(
                depsgraph, ray_origin, ray_world
            )
            print(f"DEBUG: hit={hit}, location={location if hit else None}, obj={obj if hit else None}")
            
            if hit:
                # Verify hit distance is reasonable (street-level views are close)
                dist = (location - ray_origin).length
                print(f"DEBUG: hit distance={dist:.2f} meters")
                if dist < 60.0:  # within 60 meters
                    # Convert Blender coordinates to True ENU
                    bx, by, bz = location
                    east = bx
                    north = by - SHIFT_NORTH
                    
                    # Note: We don't shift height (Z) in our ENU coordinate system,
                    # because height inside Blender matches the game's Y height (3356m base).
                    # Let's save both Blender and True ENU coords
                    detections_3d.append({
                        "viewpoint_id": vp_id,
                        "glb_path": glb_path,
                        "class_name": det["class_name"],
                        "confidence": det["confidence"],
                        "distance_meters": round(dist, 2),
                        # 3D Position in Blender mesh space
                        "pos_blender": [round(bx, 2), round(by, 2), round(bz, 2)],
                        # 3D Position in True ENU space (aligned with OSM roads)
                        "pos_enu": [round(east, 2), round(north, 2), round(bz, 2)],
                    })
                else:
                    print("DEBUG: skipped hit because distance > 60m")
    print(f"Total 3D points projected: {len(detections_3d)}")
    # Save results
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(detections_3d, f, indent=2)
        
    print(f"Saved {len(detections_3d)} projected 3D points to {OUTPUT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
