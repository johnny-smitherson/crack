import bpy
import sys
import json
import os
import numpy as np

# Shift constant to convert Blender coordinates back to True ENU
SHIFT_NORTH = 21392.2


def flatten_tile_meshes(glb_path, patched_glb_path, obstacles):
    """
    Load a GLB, find vertices in obstacle regions, interpolate height,
    flatten, and save.
    """
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb_path))
    except Exception as e:
        print(f"Failed to load GLB {glb_path}: {e}")
        return False
        
    scene = bpy.context.scene
    
    # Find all meshes in the scene
    meshes = [obj for obj in scene.objects if obj.type == 'MESH']
    if not meshes:
        print("No meshes found in GLB")
        return False
        
    # Build list of obstacle points in Blender coordinates
    # Obstacle coordinate format in JSON is [east, north, up]
    # In Blender: X = East, Y = North + SHIFT_NORTH
    obs_list = []
    for obs in obstacles:
        oe, on, oz = obs["pos_enu"]
        cls_name = obs["class_name"]
        
        # Determine radius based on class
        if cls_name == "car":
            radius = 3.0
        elif cls_name in ("truck", "bus"):
            radius = 6.0
        elif cls_name == "motorcycle":
            radius = 1.5
        elif cls_name == "tree":
            radius = 2.5
        else:
            radius = 3.0
            
        obs_list.append({
            "bx": oe,
            "by": on + SHIFT_NORTH,
            "bz": oz,
            "radius": radius,
            "class_name": cls_name,
        })
        
    total_vertices_flattened = 0
    
    # Process each mesh
    for obj in meshes:
        mesh = obj.data
        matrix = obj.matrix_world
        
        # We need to compute world-space vertex locations to check boundaries and heights,
        # but modify the local vertex coordinates.
        inv_matrix = matrix.inverted()
        
        # Get all vertices
        vertices = mesh.vertices
        n_verts = len(vertices)
        
        # Convert all vertices to world space
        world_coords = np.zeros((n_verts, 3))
        for i, v in enumerate(vertices):
            world_coords[i] = matrix @ v.co
            
        # For each obstacle, find vertices to flatten and calculate local ground height
        for obs in obs_list:
            ox, oy, oz, radius = obs["bx"], obs["by"], obs["bz"], obs["radius"]
            
            # Find vertices within the obstacle radius (in 2D X-Y plane)
            dist_2d = np.linalg.norm(world_coords[:, :2] - np.array([ox, oy]), axis=1)
            
            # Height limit to avoid flattening trees/overhangs/canopies
            # We only flatten vertices that are close to the ground height oz (e.g., within -1.0 to +2.2m)
            height_diff = world_coords[:, 2] - oz
            to_flatten = (dist_2d <= radius) & (height_diff >= -1.0) & (height_diff <= 2.2)
            
            if not np.any(to_flatten):
                continue
                
            # Find boundary vertices: outside obstacle radius, but within radius + 2.0 meters.
            # We use their heights to interpolate the flat ground.
            boundary_verts = (dist_2d > radius) & (dist_2d <= radius + 2.0) & (height_diff >= -1.0) & (height_diff <= 1.0)
            
            if np.any(boundary_verts):
                # Median height of the boundary road surface
                target_z = np.median(world_coords[boundary_verts, 2])
            else:
                # Fallback to the median height of all vertices
                target_z = np.median(world_coords[:, 2])
                    
            # Apply flattening
            flatten_indices = np.where(to_flatten)[0]
            for idx in flatten_indices:
                # Set world Z coordinate
                # For vertices that are slightly above target_z but below the threshold,
                # we flatten them completely to the target_z.
                world_pos = Vector((world_coords[idx, 0], world_coords[idx, 1], target_z))
                # Convert back to local mesh coordinates
                local_pos = inv_matrix @ world_pos
                vertices[idx].co = local_pos
                total_vertices_flattened += 1
                
        # Update mesh geometry
        mesh.update()
        
    # Export patched GLB
    if total_vertices_flattened > 0:
        os.makedirs(os.path.dirname(patched_glb_path), exist_ok=True)
        try:
            bpy.ops.export_scene.gltf(
                filepath=os.path.abspath(patched_glb_path),
                export_format='GLB',
                use_selection=False,
            )
            print(f"FLATTEN_OK: Flattened {total_vertices_flattened} vertices in {glb_path} -> {patched_glb_path}")
            return True
        except Exception as e:
            print(f"Failed to export patched GLB: {e}")
            return False
    else:
        print(f"FLATTEN_SKIP: No vertices to flatten in {glb_path}")
        return True


def main():
    try:
        args_idx = sys.argv.index("--")
        args = sys.argv[args_idx + 1:]
    except ValueError:
        args = []

    if len(args) < 1:
        print("Usage: blender -b -P flatten_mesh.py -- <batch_json_path>")
        sys.exit(1)

    batch_path = args[0]
    with open(batch_path, "r", encoding="utf-8") as f:
        batch = json.load(f)

    # Let's import mathutils Vector
    global Vector
    from mathutils import Vector

    tiles = batch.get("tiles", [])
    
    succeeded = 0
    failed = 0
    for tile in tiles:
        glb_path = tile["glb_path"]
        patched_path = tile["patched_glb_path"]
        obstacles = tile["obstacles"]
        
        try:
            if flatten_tile_meshes(glb_path, patched_path, obstacles):
                succeeded += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error processing tile {glb_path}: {e}")
            failed += 1

    print(f"Batch complete: {succeeded} succeeded, {failed} failed (of {len(tiles)})")


if __name__ == "__main__":
    main()
