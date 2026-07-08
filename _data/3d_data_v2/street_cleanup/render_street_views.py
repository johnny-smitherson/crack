"""
Blender street-level renderer (optimized batch version).

Loads all unique GLB files for a batch once, positions a perspective camera
at street level for each viewpoint, and renders the view.
"""

import bpy
import sys
import json
import math
import os
import time
import numpy as np

# Constant shifts to convert True ENU coordinates to GLB mesh space
SHIFT_NORTH = 21392.2


def find_ground_height(x, y, fallback_z=3360.0):
    """Cast a vertical ray down from above to find the mesh surface height."""
    scene = bpy.context.scene
    depsgraph = bpy.context.view_layer.depsgraph
    
    # Start ray well above the mesh (Z max in Bucharest is ~3400m)
    origin = (x, y, 3500.0)
    direction = (0.0, 0.0, -1.0)
    
    # Cast ray
    hit, location, normal, index, obj, matrix = scene.ray_cast(
        depsgraph, origin, direction
    )
    
    if hit:
        return location[2]
    return fallback_z


def setup_scene_for_batch(glb_paths):
    """Load all GLB files into a clean scene and convert materials."""
    # 1. Clear scene
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    except Exception as e:
        print(f"Failed to read factory settings: {e}")
        return False

    # 2. Import all GLBs
    imported_any = False
    for path in glb_paths:
        try:
            bpy.ops.import_scene.gltf(filepath=os.path.abspath(path))
            imported_any = True
        except Exception as e:
            print(f"Failed to load GLB {path}: {e}")

    if not imported_any:
        print("Failed to load any GLB files")
        return False

    # 3. Convert materials to unlit (Emission)
    for mat in bpy.data.materials:
        if mat.use_nodes:
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            node_tex = None
            node_output = None
            for node in nodes:
                if node.type == 'TEX_IMAGE':
                    node_tex = node
                elif node.type == 'OUTPUT_MATERIAL':
                    node_output = node
                    
            if node_tex and node_output:
                for node in list(nodes):
                    if node != node_tex and node != node_output:
                        nodes.remove(node)
                        
                node_emit = nodes.new(type="ShaderNodeEmission")
                links.new(node_tex.outputs["Color"], node_emit.inputs["Color"])
                links.new(node_emit.outputs["Emission"], node_output.inputs["Surface"])

    # 4. Render setup (EEVEE)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    
    # Set background color
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg_node = scene.world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.7, 0.8, 0.9, 1.0)  # sky blue background
        
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640

    # 5. Create Camera
    cam_data = bpy.data.cameras.new(name="Camera")
    cam_data.type = 'PERSP'
    cam_data.lens = 24.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 150.0
    
    cam_obj = bpy.data.objects.new(name="Camera", object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # 6. Create Target
    target_obj = bpy.data.objects.new(name="Target", object_data=None)
    bpy.context.collection.objects.link(target_obj)

    # 7. Setup track constraint
    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = target_obj
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    return cam_obj, target_obj


def render_viewpoint(vp, cam_obj, target_obj):
    """Render a single viewpoint to JPG and write metadata using existing objects."""
    out_jpg = vp["jpg_path"]
    out_meta = vp["meta_path"]
    glb_paths = vp.get("glb_paths", [vp["glb_path"]])
    
    # Convert True ENU to Blender mesh coordinates
    ve = vp["east"]
    vn = vp["north"]
    heading_deg = vp["heading_deg"]
    
    bx = ve
    by = vn + SHIFT_NORTH
    
    # 1. Update view layer to build depsgraph for raycasting
    bpy.context.view_layer.update()
    bz = find_ground_height(bx, by)
    
    # 2. Position Camera
    cam_obj.location = (bx, by, bz + 1.8)
    
    # 3. Position Target
    heading_rad = math.radians(heading_deg)
    tx = bx + 15.0 * math.cos(heading_rad)
    ty = by + 15.0 * math.sin(heading_rad)
    tz = bz
    target_obj.location = (tx, ty, tz)
    
    # Update view layer again to apply tracking constraint
    bpy.context.view_layer.update()
    
    # 4. Render
    scene = bpy.context.scene
    scene.render.filepath = os.path.abspath(out_jpg)
    bpy.ops.render.render(write_still=True)
    
    # 5. Save viewpoint metadata (including camera matrix and FOV for back-projection)
    matrix_world = np.array(cam_obj.matrix_world)
    cam_data = cam_obj.data
    
    meta = {
        "viewpoint_id": vp["id"],
        "glb_path": glb_paths[0],
        "glb_paths": glb_paths,
        "camera_pos_blender": [float(bx), float(by), float(bz + 1.8)],
        "target_pos_blender": [float(tx), float(ty), float(tz)],
        "ground_height_blender": float(bz),
        "matrix_world": matrix_world.tolist(),
        "camera_fov": float(cam_data.angle),
        "clip_start": float(cam_data.clip_start),
        "clip_end": float(cam_data.clip_end),
        "resolution": [640, 640],
    }
    with open(out_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        
    return True


def main():
    try:
        args_idx = sys.argv.index("--")
        args = sys.argv[args_idx + 1:]
    except ValueError:
        args = []

    if len(args) < 1:
        print("Usage: blender -b -P render_street_views.py -- <batch_json_path>")
        sys.exit(1)

    batch_path = args[0]
    with open(batch_path, "r", encoding="utf-8") as f:
        batch = json.load(f)

    viewpoints = batch.get("viewpoints", [])
    if not viewpoints:
        print("No viewpoints to render")
        sys.exit(0)

    # Collect all unique GLB files for the batch
    all_glb_paths = set()
    for vp in viewpoints:
        for p in vp.get("glb_paths", [vp["glb_path"]]):
            all_glb_paths.add(p)
            
    print(f"Batch has {len(viewpoints)} viewpoints. Total unique GLB files to load: {len(all_glb_paths)}")
    
    # Setup batch scene once
    t0 = time.time()
    res = setup_scene_for_batch(sorted(list(all_glb_paths)))
    if not res:
        print("Failed to setup batch scene")
        sys.exit(1)
    cam_obj, target_obj = res
    print(f"Batch scene setup complete in {time.time() - t0:.1f}s")
    
    rendered = 0
    failed = 0
    for vp in viewpoints:
        vp_id = vp["id"]
        try:
            if render_viewpoint(vp, cam_obj, target_obj):
                rendered += 1
                print(f"RENDER_OK {vp_id}")
            else:
                failed += 1
                print(f"RENDER_FAIL {vp_id}")
        except Exception as e:
            failed += 1
            print(f"RENDER_FAIL {vp_id}: {e}")

    print(f"Batch complete: {rendered} rendered, {failed} failed (of {len(viewpoints)})")


if __name__ == "__main__":
    main()
