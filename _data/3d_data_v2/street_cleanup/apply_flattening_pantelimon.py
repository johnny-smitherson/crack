#!/usr/bin/env python3
"""
Global flattening script for Șoseaua Pantelimon main road.
Identifies intersecting depth-20 tiles, renders them top-down, runs YOLOv7 ONNX detection,
filters detections to the road surface, flattens the GLB vertices in-place, and rebuilds the manifest.
"""

import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np
import pyarrow.parquet as pq
import shapely.wkb
import trimesh
from shapely.geometry import Point, LineString, box as shapely_box
from shapely.ops import unary_union

# Add parent directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from street_cleanup.coord_utils import (
    latlon_to_enu,
    latlon_coords_to_enu,
    pixel_to_blender_xyz,
    bbox_center_blender_xyz,
)
from street_cleanup.road_tiles import glb_path_for_octant

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("flatten_pantelimon")

# Paths
ROOT_DIR = Path(__file__).resolve().parents[2]
ONNX_PATH = ROOT_DIR / "_slop" / "detection_sandbox" / "yolov7-m_itcvd_qgis.onnx"
ROADS_GEOJSON = Path("data_osm/roads.geojson")
MANIFEST_PATH = Path("data_out/manifest.parquet")
RENDER_SCRIPT = Path("street_cleanup/render_top_down.py")

CONF_THRESHOLD = 0.25
BLENDER_BATCH_SIZE = 16
MAX_WORKERS = 4


def load_pantelimon_road_polygon() -> shapely.geometry.MultiPolygon:
    """Loads and returns the buffered road polygon of Soseaua Pantelimon in ENU coordinates."""
    if not ROADS_GEOJSON.exists():
        logger.error(f"Roads GeoJSON not found: {ROADS_GEOJSON}")
        sys.exit(1)

    with open(ROADS_GEOJSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    p_lines = []
    for f in data.get("features", []):
        if f.get("properties", {}).get("tags", {}).get("name") == "Șoseaua Pantelimon":
            geom = f["geometry"]
            if geom["type"] == "LineString":
                p_lines.append(LineString(latlon_coords_to_enu(geom["coordinates"])))
            elif geom["type"] == "MultiLineString":
                for line in geom["coordinates"]:
                    p_lines.append(LineString(latlon_coords_to_enu(line)))

    if not p_lines:
        logger.error("No OSM segments found for street 'Șoseaua Pantelimon'")
        sys.exit(1)

    # Buffer by 6.5 meters on each side to cover lanes and sidewalks/curbs
    road_polygons = [line.buffer(6.5, cap_style="flat", join_style="mitre") for line in p_lines]
    merged = unary_union(road_polygons)
    shapely.prepare(merged)
    return merged


def load_pantelimon_road_polygon_12m() -> shapely.geometry.MultiPolygon:
    """Loads and returns the buffered road polygon of Soseaua Pantelimon with 12m buffer in ENU coordinates."""
    if not ROADS_GEOJSON.exists():
        logger.error(f"Roads GeoJSON not found: {ROADS_GEOJSON}")
        sys.exit(1)

    with open(ROADS_GEOJSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    p_lines = []
    for f in data.get("features", []):
        if f.get("properties", {}).get("tags", {}).get("name") == "Șoseaua Pantelimon":
            geom = f["geometry"]
            if geom["type"] == "LineString":
                p_lines.append(LineString(latlon_coords_to_enu(geom["coordinates"])))
            elif geom["type"] == "MultiLineString":
                for line in geom["coordinates"]:
                    p_lines.append(LineString(latlon_coords_to_enu(line)))

    if not p_lines:
        logger.error("No OSM segments found for street 'Șoseaua Pantelimon'")
        sys.exit(1)

    road_polygons = [line.buffer(12.0, cap_style="flat", join_style="mitre") for line in p_lines]
    merged = unary_union(road_polygons)
    shapely.prepare(merged)
    return merged


def load_street_trees(road_poly_12m: shapely.geometry.MultiPolygon) -> list[tuple[float, float]]:
    """Loads and returns all OSM trees (as ENU coordinates) within 12m of Soseaua Pantelimon."""
    natural_geojson = Path("data_osm/natural.geojson")
    if not natural_geojson.exists():
        logger.warning(f"natural.geojson not found, skipping tree flattening.")
        return []

    with open(natural_geojson, "r", encoding="utf-8") as f:
        data = json.load(f)

    trees = []
    for feat in data.get("features", []):
        tags = feat.get("properties", {}).get("tags", {})
        if tags.get("natural") == "tree":
            geom = feat.get("geometry", {})
            if geom.get("type") == "Point":
                lon, lat = geom["coordinates"]
                east, north = latlon_to_enu(lat, lon)
                pt = Point(east, north)
                if road_poly_12m.contains(pt):
                    trees.append((east, north))

    logger.info(f"Loaded {len(trees)} roadside trees from OSM.")
    return trees


def get_pantelimon_tiles(road_poly: shapely.geometry.MultiPolygon) -> list[dict]:
    """Finds all depth-20 tiles in the manifest that intersect Soseaua Pantelimon."""
    if not MANIFEST_PATH.exists():
        logger.error(f"Manifest not found: {MANIFEST_PATH}")
        sys.exit(1)

    logger.info("Loading manifest and checking tile intersections...")
    table = pq.read_table(MANIFEST_PATH)
    rows = table.to_pylist()

    intersecting = []
    for r in rows:
        if r["depth"] == 20:
            east_min, north_min = latlon_to_enu(r["lat_south"], r["lon_west"])
            east_max, north_max = latlon_to_enu(r["lat_north"], r["lon_east"])
            tile_box = shapely_box(east_min, north_min, east_max, north_max)
            if road_poly.intersects(tile_box):
                intersecting.append(r)

    logger.info(f"Found {len(intersecting)} intersecting depth-20 tiles out of {len(rows)} total manifest rows.")
    return intersecting


def tile_to_render_spec(tile: dict) -> dict:
    glb_path = glb_path_for_octant(tile["octant_path"])
    last_three = tile["octant_path"][-3:]
    render_dir = Path("street_cleanup/renders") / last_three
    return {
        "octant_path": tile["octant_path"],
        "glb_path": str(glb_path),
        "jpg_path": str(render_dir / f"{tile['octant_path']}.jpg"),
        "meta_path": str(render_dir / f"{tile['octant_path']}.json"),
        "lat_lon_bbox": {
            "lat_south": tile["lat_south"],
            "lat_north": tile["lat_north"],
            "lon_west": tile["lon_west"],
            "lon_east": tile["lon_east"],
        },
        "resolution": [1024, 1024],
    }


def run_blender_batch(batch_tiles: list[dict]) -> tuple[int, int]:
    spec = {"tiles": batch_tiles}
    with tempfile.NamedTemporaryFile("w", suffix=".json", prefix="topdown_batch_", delete=False) as tf:
        json.dump(spec, tf)
        tf_name = tf.name

    cmd = ["blender", "-b", "-P", str(RENDER_SCRIPT), "--", tf_name]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(tf_name):
            os.remove(tf_name)

        output = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            logger.error("Blender process failed (code=%s)\n%s", proc.returncode, output[-1000:])
            return 0, len(batch_tiles)

        success_count = output.count("RENDER_OK")
        fail_count = output.count("RENDER_FAIL")
        return success_count, fail_count
    except Exception as exc:
        logger.error("Error running Blender batch: %s", exc)
        if os.path.exists(tf_name):
            os.remove(tf_name)
        return 0, len(batch_tiles)


def run_yolov7_onnx(image_path: Path, net) -> list[dict]:
    """Runs YOLOv7 ONNX model on the image and returns detections."""
    img = cv2.imread(str(image_path))
    if img is None:
        return []
    h_img, w_img, _ = img.shape

    blob = cv2.dnn.blobFromImage(img, 1.0 / 255.0, (640, 640), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward()

    predictions = outputs[0]
    raw_detections = []

    for pred in predictions:
        obj_conf = pred[4]
        class_prob = pred[5]
        confidence = obj_conf * class_prob

        if confidence >= CONF_THRESHOLD:
            x_c, y_c, w, h = pred[0:4]
            x_c = (x_c / 640.0) * w_img
            y_c = (y_c / 640.0) * h_img
            w = (w / 640.0) * w_img
            h = (h / 640.0) * h_img

            x1 = int(x_c - w / 2)
            y1 = int(y_c - h / 2)
            x2 = int(x_c + w / 2)
            y2 = int(y_c + h / 2)

            raw_detections.append({
                "bbox_pixel": [x1, y1, x2, y2],
                "confidence": float(confidence),
            })

    # NMS
    boxes = []
    scores = []
    for det in raw_detections:
        x1, y1, x2, y2 = det["bbox_pixel"]
        boxes.append([x1, y1, x2 - x1, y2 - y1])
        scores.append(det["confidence"])

    indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.01, nms_threshold=0.4)
    if len(indices) > 0:
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()
        elif isinstance(indices[0], (list, tuple, np.ndarray)):
            indices = [idx[0] for idx in indices]
        return [raw_detections[idx] for idx in indices]
    return []


def main():
    logger.info("=" * 60)
    logger.info("Șoseaua Pantelimon Global Cleanup & Flattening Pipeline")
    logger.info("=" * 60)

    # 1. Load Soseaua Pantelimon road polygons
    road_poly = load_pantelimon_road_polygon()
    road_poly_12m = load_pantelimon_road_polygon_12m()
    logger.info("Loaded Șoseaua Pantelimon road surface geometries.")

    # Load OSM roadside trees
    street_trees = load_street_trees(road_poly_12m)

    # 2. Get intersecting tiles
    tiles = get_pantelimon_tiles(road_poly)
    if not tiles:
        logger.warning("No intersecting tiles found. Exiting.")
        return

    # 3. Compile render specs and find missing renders
    render_specs = [tile_to_render_spec(t) for t in tiles]
    todo_renders = []
    for spec in render_specs:
        jpg_path = Path(spec["jpg_path"])
        meta_path = Path(spec["meta_path"])
        if not (jpg_path.exists() and meta_path.exists()):
            todo_renders.append(spec)

    logger.info(f"Already rendered: {len(render_specs) - len(todo_renders)}")
    logger.info(f"Remaining to render: {len(todo_renders)}")

    # 4. Render top-down images in parallel batches
    if todo_renders:
        batches = [todo_renders[i : i + BLENDER_BATCH_SIZE] for i in range(0, len(todo_renders), BLENDER_BATCH_SIZE)]
        logger.info(f"Dividing rendering work into {len(batches)} batches...")
        total_ok = 0
        total_fail = 0
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(run_blender_batch, batch): batch for batch in batches}
            for i, future in enumerate(as_completed(futures), start=1):
                ok, fail = future.result()
                total_ok += ok
                total_fail += fail
                logger.info(f"Progress: {i}/{len(batches)} batches | Rendered OK: {total_ok}, Failed: {total_fail}")
        logger.info(f"Rendering complete in {time.time() - t0:.1f}s.")

    # 5. Load YOLOv7 ONNX model
    if not ONNX_PATH.exists():
        logger.error(f"YOLOv7 ONNX model weights not found at: {ONNX_PATH}")
        sys.exit(1)
    logger.info(f"Loading YOLOv7 ONNX model from: {ONNX_PATH.name}")
    net = cv2.dnn.readNetFromONNX(str(ONNX_PATH))

    # 6. Process each tile: run YOLO, check OSM trees, filter to road, apply trimesh flattening
    tiles_modified = 0
    total_vertices_flattened = 0
    logger.info("Running cleanup and mesh flattening on tiles...")

    for i, spec in enumerate(render_specs, start=1):
        jpg_path = Path(spec["jpg_path"])
        meta_path = Path(spec["meta_path"])
        glb_path = Path(spec["glb_path"])

        if not (jpg_path.exists() and meta_path.exists() and glb_path.exists()):
            continue

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        # Filter detections to the Soseaua Pantelimon road polygon
        width, height = meta["resolution"]
        bbox_xyz = meta["bbox_xyz"]
        x_min, y_min, z_min = bbox_xyz["min"]
        x_max, y_max, z_max = bbox_xyz["max"]

        # Run detection
        detections = run_yolov7_onnx(jpg_path, net)
        filtered_detections = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox_pixel"]
            bx, by, bz = bbox_center_blender_xyz(x1, y1, x2, y2, width, height, bbox_xyz)
            if road_poly.contains(Point(bx, by)):
                filtered_detections.append(det)

        # Check for OSM trees inside the tile
        tile_trees = []
        for east, north in street_trees:
            if x_min <= east <= x_max and y_min <= north <= y_max:
                tile_trees.append((east, north))

        if not filtered_detections and not tile_trees:
            continue

        # Load GLB to apply flattening
        scene = trimesh.load(str(glb_path))
        if "mesh_0" not in scene.geometry:
            continue
        mesh = scene.geometry["mesh_0"]
        vertices = mesh.vertices.copy()

        # Backup the original GLB if no backup exists
        bak_path = glb_path.with_suffix(".glb.bak")
        if not bak_path.exists():
            import shutil
            shutil.copyfile(glb_path, bak_path)

        tile_vertices_flattened = 0

        # Flatten detected cars
        for det in filtered_detections:
            x1, y1, x2, y2 = det["bbox_pixel"]

            # Translate pixel bounding box to Blender coordinates
            x_min_world = x_min + (x1 / width) * (x_max - x_min)
            x_max_world = x_min + (x2 / width) * (x_max - x_min)
            y_min_world = y_max - (y2 / height) * (y_max - y_min)
            y_max_world = y_max - (y1 / height) * (y_max - y_min)

            # Vertex mask in GLB space
            mask = (
                (vertices[:, 0] >= x_min_world) & (vertices[:, 0] <= x_max_world) &
                (vertices[:, 2] >= -y_max_world) & (vertices[:, 2] <= -y_min_world)
            )

            # Boundary ring expanded by 1.2 meters to sample surrounding road height
            buffer_m = 1.2
            x_min_ring = x_min_world - buffer_m
            x_max_ring = x_max_world + buffer_m
            y_min_ring = y_min_world - buffer_m
            y_max_ring = y_max_world + buffer_m

            ring_mask = (
                (vertices[:, 0] >= x_min_ring) & (vertices[:, 0] <= x_max_ring) &
                (vertices[:, 2] >= -y_max_ring) & (vertices[:, 2] <= -y_min_ring) &
                ~mask
            )

            in_count = np.sum(mask)
            if in_count == 0:
                continue

            ring_count = np.sum(ring_mask)
            if ring_count > 0:
                target_height = np.median(vertices[ring_mask, 1])
            else:
                target_height = np.median(vertices[mask, 1])

            vertices[mask, 1] = target_height
            tile_vertices_flattened += in_count

        # Flatten OSM trees
        for east, north in tile_trees:
            tree_radius = 2.25
            east_min = east - tree_radius
            east_max = east + tree_radius
            north_min = north - tree_radius
            north_max = north + tree_radius

            # Vertex mask in GLB space (GLB Z = -North)
            mask = (
                (vertices[:, 0] >= east_min) & (vertices[:, 0] <= east_max) &
                (vertices[:, 2] >= -north_max) & (vertices[:, 2] <= -north_min)
            )

            # Boundary ring expanded by 1.2 meters to sample surrounding road height
            buffer_m = 1.2
            east_min_ring = east_min - buffer_m
            east_max_ring = east_max + buffer_m
            north_min_ring = north_min - buffer_m
            north_max_ring = north_max + buffer_m

            ring_mask = (
                (vertices[:, 0] >= east_min_ring) & (vertices[:, 0] <= east_max_ring) &
                (vertices[:, 2] >= -north_max_ring) & (vertices[:, 2] <= -north_min_ring) &
                ~mask
            )

            in_count = np.sum(mask)
            if in_count == 0:
                continue

            ring_count = np.sum(ring_mask)
            if ring_count > 0:
                target_height = np.median(vertices[ring_mask, 1])
            else:
                target_height = np.median(vertices[mask, 1])

            vertices[mask, 1] = target_height
            tile_vertices_flattened += in_count

        if tile_vertices_flattened > 0:
            mesh.vertices = vertices
            scene.export(str(glb_path))
            tiles_modified += 1
            total_vertices_flattened += tile_vertices_flattened
            logger.info(f"Patched GLB {glb_path.name}: flattened {tile_vertices_flattened} vertices (cars/trees).")

        if i % 50 == 0 or i == len(render_specs):
            logger.info(f"Processed {i}/{len(render_specs)} tiles...")

    logger.info("=" * 60)
    logger.info("CLEANUP SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tiles modified: {tiles_modified}")
    logger.info(f"Total vertices flattened: {total_vertices_flattened}")
    logger.info("=" * 60)

    # 7. Rebuild manifest parquet
    logger.info("Rebuilding manifest.parquet...")
    cmd = ["uv", "run", "python", "rebuild_manifest.py"]
    subprocess.run(cmd, cwd=str(ROOT_DIR / "_data" / "3d_data_v2"))
    logger.info("Manifest rebuilt successfully.")


if __name__ == "__main__":
    main()
