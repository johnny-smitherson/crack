"""
Orchestrates Blender street-level rendering in batches and parallel processes.

Loads filtered_viewpoints.json, batches them, and spawns multiple headless
Blender processes to perform the rendering using Cycles.

Supports a --limit flag to run a quick test on a small subset of viewpoints.

Run from _data/3d_data_v2/:
    uv run python street_cleanup/run_renders.py --limit 100
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
from street_cleanup.coord_utils import latlon_to_enu

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("run_renders")

FILTERED_VIEWPOINTS_PATH = Path("street_cleanup/filtered_viewpoints.json")
RENDERS_DIR = Path("street_cleanup/renders")

# Render process settings
BLENDER_BATCH_SIZE = 16  # viewpoints per single Blender process
MAX_WORKERS = 4         # parallel Blender processes


def run_blender_batch(batch_viewpoints):
    """Run Blender for a batch of viewpoints."""
    spec = {"viewpoints": batch_viewpoints}
    
    with tempfile.NamedTemporaryFile("w", suffix=".json", prefix="blender_vp_", delete=False) as tf:
        json.dump(spec, tf)
        tf_name = tf.name
        
    cmd = [
        "blender",
        "-b",
        "-P",
        "street_cleanup/render_street_views.py",
        "--",
        tf_name,
    ]
    
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        # Clean up temp file
        if os.path.exists(tf_name):
            os.remove(tf_name)
            
        if proc.returncode != 0:
            logger.error(f"Blender process failed (code={proc.returncode})")
            return len(batch_viewpoints), 0
            
        # Count successful renders in stdout
        output = proc.stdout or ""
        success_count = output.count("RENDER_OK")
        fail_count = output.count("RENDER_FAIL")
        
        logger.info(f"Batch completed in {time.time() - t0:.1f}s: {success_count} OK, {fail_count} Failed")
        return success_count, fail_count
    except Exception as e:
        logger.error(f"Error running Blender batch: {e}")
        if os.path.exists(tf_name):
            os.remove(tf_name)
        return 0, len(batch_viewpoints)


def main():
    parser = argparse.ArgumentParser(description="Orchestrate Blender street-level rendering.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of viewpoints to render (0 for all)")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="Number of parallel Blender processes")
    parser.add_argument("--force", action="store_true", help="Force re-rendering of all viewpoints even if they exist")
    parser.add_argument("--road", type=str, default="", help="Filter viewpoints by road name (case-insensitive substring)")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Starting Street-Level Renderer Orchestrator")
    logger.info("=" * 60)

    if not FILTERED_VIEWPOINTS_PATH.exists():
        logger.error(f"Filtered viewpoints not found: {FILTERED_VIEWPOINTS_PATH}")
        logger.error("Run sample_camera_positions.py and filter_viewpoints.py first!")
        sys.exit(1)

    # Ensure output directories exist
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)

    # Load viewpoints
    with open(FILTERED_VIEWPOINTS_PATH, "r", encoding="utf-8") as f:
        viewpoints = json.load(f)

    # Load manifest to find surrounding tiles
    logger.info("Loading manifest.parquet to compute surrounding tiles...")
    manifest_table = pq.read_table("data_out/manifest.parquet")
    manifest_rows = manifest_table.to_pylist()
    
    candidate_tiles = []
    for r in manifest_rows:
        if r["depth"] in (19, 20):
            e_min, n_min = latlon_to_enu(r["lat_south"], r["lon_west"])
            e_max, n_max = latlon_to_enu(r["lat_north"], r["lon_east"])
            candidate_tiles.append({
                "octant_path": r["octant_path"],
                "glb_path": r["glb_path"],
                "depth": r["depth"],
                "center": np.array([(e_min + e_max)/2, (n_min + n_max)/2])
            })
    logger.info(f"Loaded {len(candidate_tiles)} candidate tiles for radius mapping.")

    # Filter out viewpoints that already have JPG and JSON files
    todo_viewpoints = []
    for vp in viewpoints:
        # Apply road filter if specified
        if args.road and args.road.lower() not in vp["road_name"].lower():
            continue

        vp_id = vp["id"]
        jpg_path = RENDERS_DIR / f"{vp_id}.jpg"
        meta_path = RENDERS_DIR / f"{vp_id}.json"
        
        if args.force or not (jpg_path.exists() and meta_path.exists()):
            vp_modified = vp.copy()
            vp_modified["jpg_path"] = str(jpg_path)
            vp_modified["meta_path"] = str(meta_path)
            
            # Find surrounding tiles within 80m radius
            ve, vn = vp["east"], vp["north"]
            vp_center = np.array([ve, vn])
            
            matched = []
            for t in candidate_tiles:
                dist = np.linalg.norm(t["center"] - vp_center)
                if dist <= 80.0:
                    matched.append(t)
            
            # Hierarchical filtering: discard parent if a child is present
            matched_paths = {t["octant_path"] for t in matched}
            final_matched = []
            for t in matched:
                p = t["octant_path"]
                has_finer = any(other.startswith(p) and len(other) > len(p) for other in matched_paths)
                if not has_finer:
                    final_matched.append(t)
            
            if not final_matched:
                vp_modified["glb_paths"] = [vp["glb_path"]]
            else:
                vp_modified["glb_paths"] = [t["glb_path"] for t in final_matched]
                
            todo_viewpoints.append(vp_modified)

    total_existing = len(viewpoints) - len(todo_viewpoints)
    logger.info(f"Total viewpoints in config: {len(viewpoints)}")
    logger.info(f"Already rendered: {total_existing}")
    logger.info(f"Remaining to render: {len(todo_viewpoints)}")

    if not todo_viewpoints:
        logger.info("Nothing to render! All viewpoints already generated.")
        sys.exit(0)

    # Apply limit if specified
    if args.limit > 0:
        todo_viewpoints = todo_viewpoints[:args.limit]
        logger.info(f"Limiting render queue to {args.limit} viewpoints (--limit flag).")

    # Batch viewpoints
    batches = [todo_viewpoints[i:i + BLENDER_BATCH_SIZE] for i in range(0, len(todo_viewpoints), BLENDER_BATCH_SIZE)]
    logger.info(f"Divided work into {len(batches)} batches of size {BLENDER_BATCH_SIZE}...")

    # Spawn workers
    total_rendered = 0
    total_failed = 0
    t_start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_blender_batch, b): b for b in batches}
        
        for i, future in enumerate(as_completed(futures), start=1):
            success, fail = future.result()
            total_rendered += success
            total_failed += fail
            
            pct = (i / len(batches)) * 100.0
            elapsed = time.time() - t_start
            eta = (elapsed / i) * (len(batches) - i) if i > 0 else 0.0
            
            logger.info(
                f"Progress: {i}/{len(batches)} batches ({pct:.1f}%) | "
                f"Total OK: {total_rendered}, Fail: {total_failed} | "
                f"Elapsed: {elapsed:.1f}s, ETA: {eta:.1f}s"
            )

    logger.info("=" * 60)
    logger.info("RENDERING PROCESS COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Successfully rendered: {total_rendered}")
    logger.info(f"Failed: {total_failed}")
    logger.info(f"Total time: {time.time() - t_start:.1f}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
