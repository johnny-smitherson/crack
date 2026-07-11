"""
Targeted Downloader for Șoseaua Pantelimon Depth 20 Tiles.

Finds all depth 20 tiles online that overlap with Șoseaua Pantelimon,
filters out already downloaded ones, and downloads + builds the missing ones.
"""

import os
import time
import json
import math
import queue
import logging
import tempfile
import threading
import numpy as np
from pathlib import Path
import subprocess
import hashlib

import pyarrow as pa
import pyarrow.parquet as pq
import shapely.wkb
from shapely.geometry import box as shapely_box

from octree import parse_bbox, BBox, octant_path_to_bbox
from earth_client import (
    fetch_planetoid_metadata,
    resolve_node,
    download_node,
    find_tiles_in_bbox_levels,
)
from mesh_decoder import decode_node
from street_cleanup.coord_utils import latlon_to_enu

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("download_pantelimon_d20")

# Configuration
BBOX_FILE = "data_in/zone-bbox.txt"
OUTPUT_DIR = "data_out"
ROAD_POLYGON_WKB = "street_cleanup/road_polygons_enu.wkb"
NETWORK_WORKERS = 100
BLENDER_WORKERS = 7
BLENDER_BATCH_SIZE = 32


def run_blender_batch(script: str, batch_json_path: str) -> str:
    cmd = ["blender", "-b", "-P", script, "--", batch_json_path]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        raise RuntimeError(
            f"Blender script {script} crashed (returncode={proc.returncode}).\n"
            f"---- blender output ----\n{output.strip()}\n------------------------"
        )
    return output


def compute_reference_point(bbox) -> np.ndarray:
    lat_deg = (bbox.north + bbox.south) / 2.0
    lon_deg = (bbox.east + bbox.west) / 2.0
    
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    a = 6378137.0
    e2 = 0.00669437999014
    N = a / math.sqrt(1.0 - e2 * math.sin(lat)**2)
    x = N * math.cos(lat) * math.cos(lon)
    y = N * math.cos(lat) * math.sin(lon)
    z = N * (1.0 - e2) * math.sin(lat)
    return np.array([x, y, z])


def main():
    # 1. Parse bounding box to calculate reference point
    logger.info(f"Parsing main bounding box from {BBOX_FILE}")
    zone_bbox = parse_bbox(BBOX_FILE)
    ref_point = compute_reference_point(zone_bbox)
    logger.info(f"Reference point: {ref_point.tolist()}")

    # 2. Load road polygon
    logger.info(f"Loading road polygon from {ROAD_POLYGON_WKB}...")
    with open(ROAD_POLYGON_WKB, "rb") as f:
        road_polygon = shapely.wkb.loads(f.read())
    shapely.prepare(road_polygon)

    # Get online root epoch
    logger.info("Fetching PlanetoidMetadata...")
    planetoid = fetch_planetoid_metadata()
    root_epoch = planetoid.root_node_metadata.epoch
    logger.info(f"Root epoch: {root_epoch}")

    # 3. Șoseaua Pantelimon bounds in Lat/Lon
    p_lats = (44.4424473, 44.4488994)
    p_lons = (26.1308401, 26.1656894)
    pant_bbox = BBox(north=p_lats[1], south=p_lats[0], west=p_lons[0], east=p_lons[1])

    # 4. Find depth 20 tiles online in the bbox
    logger.info("Finding depth 20 tiles online inside Șoseaua Pantelimon bounds...")
    level_tiles = find_tiles_in_bbox_levels(pant_bbox, 20, 20, root_epoch)
    d20_tiles = level_tiles.get(20, [])
    logger.info(f"Found {len(d20_tiles)} tiles online.")

    # 5. Filter tiles that intersect the street and are missing from disk
    todo_tiles = []
    skipped_on_disk = 0
    skipped_no_intersect = 0

    for path in d20_tiles:
        tile_box = octant_path_to_bbox(path)
        e_min, n_min = latlon_to_enu(tile_box.south, tile_box.west)
        e_max, n_max = latlon_to_enu(tile_box.north, tile_box.east)
        tb = shapely_box(e_min, n_min, e_max, n_max)

        if not road_polygon.intersects(tb):
            skipped_no_intersect += 1
            continue

        # Check if already exists on disk
        depth = len(path)
        last_three = path[-3:]
        glb_path = Path(OUTPUT_DIR) / str(depth) / last_three / f"{path}.glb"

        if glb_path.exists():
            skipped_on_disk += 1
        else:
            todo_tiles.append((path, glb_path))

    logger.info(f"Filter stats:")
    logger.info(f"  No intersection with road: {skipped_no_intersect}")
    logger.info(f"  Already on disk: {skipped_on_disk}")
    logger.info(f"  Missing to download: {len(todo_tiles)}")

    if not todo_tiles:
        logger.info("All Șoseaua Pantelimon depth 20 tiles are already on disk!")
        return

    # 6. Two-stage parallel pipeline for download + Blender conversion
    total = len(todo_tiles)
    fetch_q = queue.Queue()
    process_q = queue.Queue()

    counts = {"exported": 0, "skipped": 0, "failed": 0}
    counts_lock = threading.Lock()

    def bump(key: str):
        with counts_lock:
            counts[key] += 1

    def fetch_one(index: int, octant_path: str, glb_path: Path) -> dict | None:
        progress = f"[{index + 1}/{total}]"
        node_info = resolve_node(octant_path, root_epoch)
        if node_info is None:
            bump("skipped")
            return None

        # Download node data
        node_data = download_node(node_info)
        decoded_meshes = decode_node(node_data)
        if not decoded_meshes:
            bump("skipped")
            return None

        glb_path.parent.mkdir(parents=True, exist_ok=True)

        url_path = f"NodeData/pb=!1m2!1s{node_info.path}!2u{node_info.epoch}!2e{node_info.texture_format}"
        if node_info.imagery_epoch is not None:
            url_path += f"!3u{node_info.imagery_epoch}"
        url_path += "!4b0"
        sha1 = hashlib.sha1(url_path.encode("utf-8")).hexdigest()
        json_path = Path("data_cache") / "json_decoded" / "NodeData" / sha1[:2] / f"{sha1}.json"

        return {
            "progress": progress,
            "octant_path": octant_path,
            "json_path": json_path,
            "glb_path": glb_path,
            "mesh_count": len(decoded_meshes),
            "vertex_count": sum(len(m.positions) for m in decoded_meshes),
            "triangle_count": sum(len(m.indices) // 3 for m in decoded_meshes),
        }

    def process_batch(batch: list[dict]):
        ref_list = [float(ref_point[0]), float(ref_point[1]), float(ref_point[2])]
        spec = {
            "ref_point": ref_list,
            "nodes": [
                {
                    "octant_path": it["octant_path"],
                    "json_path": str(it["json_path"]),
                    "glb_path": str(it["glb_path"]),
                }
                for it in batch
            ],
        }

        build_start = time.time()
        with tempfile.NamedTemporaryFile("w", suffix=".json", prefix="blender_batch_", delete=True) as tf:
            json.dump(spec, tf)
            tf.flush()

            try:
                run_blender_batch("build_blend.py", tf.name)
            except Exception as e:
                logger.error(f"build_blend batch crashed ({len(batch)} nodes): {e}")
                for _ in batch:
                    bump("failed")
                return

            for it in batch:
                fresh = it["glb_path"].exists() and it["glb_path"].stat().st_mtime >= build_start
                if fresh:
                    bump("exported")
                    logger.info(
                        f"{it['progress']} Saved {it['octant_path']}.glb "
                        f"({it['mesh_count']} meshes, {it['vertex_count']} verts, "
                        f"{it['triangle_count']} tris)"
                    )
                else:
                    bump("skipped")

    def network_worker():
        while True:
            task = fetch_q.get()
            try:
                if task is None:
                    return
                index, octant_path, glb_path = task
                try:
                    work = fetch_one(index, octant_path, glb_path)
                    if work is not None:
                        process_q.put(work)
                except Exception as e:
                    logger.error(f"Fetch for {octant_path} raised an exception: {e}")
                    bump("failed")
            finally:
                fetch_q.task_done()

    def blender_worker():
        while True:
            first = process_q.get()
            if first is None:
                return
            batch = [first]
            while len(batch) < BLENDER_BATCH_SIZE:
                try:
                    nxt = process_q.get_nowait()
                except queue.Empty:
                    break
                if nxt is None:
                    process_q.put(None)
                    break
                batch.append(nxt)

            try:
                process_batch(batch)
            except Exception as e:
                logger.error(f"Blender batch of {len(batch)} nodes raised: {e}")
                for _ in batch:
                    bump("failed")

    logger.info(
        f"Starting download pipeline: {NETWORK_WORKERS} net workers -> "
        f"{BLENDER_WORKERS} Blender workers..."
    )
    net_threads = [
        threading.Thread(target=network_worker, name=f"net-{i}", daemon=True)
        for i in range(NETWORK_WORKERS)
    ]
    blend_threads = [
        threading.Thread(target=blender_worker, name=f"blend-{i}", daemon=True)
        for i in range(BLENDER_WORKERS)
    ]
    for t in net_threads + blend_threads:
        t.start()

    # Enqueue tasks
    for idx, (path, glb_path) in enumerate(todo_tiles):
        fetch_q.put((idx, path, glb_path))
    for _ in net_threads:
        fetch_q.put(None)

    # Wait for net workers to finish
    for t in net_threads:
        t.join()
    for _ in blend_threads:
        process_q.put(None)
    for t in blend_threads:
        t.join()

    logger.info("=" * 60)
    logger.info(f"FINISHED: Exported {counts['exported']} new tiles to {OUTPUT_DIR}/")
    logger.info(f"  Skipped: {counts['skipped']}, Failed: {counts['failed']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
