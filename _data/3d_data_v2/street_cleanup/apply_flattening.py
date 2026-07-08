"""
Orchestrates mesh flattening across all affected tiles.

Loads projected 3D detections from yolo_detections_3d.json, groups them by GLB
tile, batches them, and calls Blender to perform local flattening on the meshes.

Output:
  - Patched GLBs under street_cleanup/patches/{depth}/{last3}/{octant_path}.glb

Run from _data/3d_data_v2/:
    uv run python street_cleanup/apply_flattening.py
"""

import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("apply_flattening")

DETECTIONS_3D_PATH = Path("street_cleanup/yolo_detections_3d.json")
PATCHES_DIR = Path("street_cleanup/patches")

# Batch settings
BLENDER_BATCH_SIZE = 16


def run_blender_batch(batch_tiles):
    """Run Blender to flatten a batch of tiles."""
    spec = {"tiles": batch_tiles}
    
    with tempfile.NamedTemporaryFile("w", suffix=".json", prefix="blender_flat_", delete=False) as tf:
        json.dump(spec, tf)
        tf_name = tf.name
        
    cmd = [
        "blender",
        "-b",
        "-P",
        "street_cleanup/flatten_mesh.py",
        "--",
        tf_name,
    ]
    
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(tf_name):
            os.remove(tf_name)
            
        if proc.returncode != 0:
            logger.error(f"Blender process failed (code={proc.returncode})")
            return 0, len(batch_tiles)
            
        output = proc.stdout or ""
        success_count = output.count("FLATTEN_OK") + output.count("FLATTEN_SKIP")
        fail_count = output.count("FLATTEN_FAIL")
        
        logger.info(f"Batch completed in {time.time() - t0:.1f}s: {success_count} succeeded, {fail_count} failed")
        return success_count, fail_count
    except Exception as e:
        logger.error(f"Error running Blender flattening: {e}")
        if os.path.exists(tf_name):
            os.remove(tf_name)
        return 0, len(batch_tiles)


def main():
    logger.info("=" * 60)
    logger.info("Starting Street Obstacle Flattening Orchestrator")
    logger.info("=" * 60)

    if not DETECTIONS_3D_PATH.exists():
        logger.error(f"Projected 3D detections not found: {DETECTIONS_3D_PATH}")
        logger.error("Run YOLO detection and project_detections.py first!")
        sys.exit(1)

    # Load detections
    with open(DETECTIONS_3D_PATH, "r", encoding="utf-8") as f:
        detections = json.load(f)
        
    logger.info(f"Loaded {len(detections)} projected 3D points.")
    if not detections:
        logger.warning("No detections to flatten. Nothing to do!")
        sys.exit(0)

    # Group detections by GLB path
    glb_groups = {}
    for d in detections:
        glb = d["glb_path"]
        glb_groups.setdefault(glb, []).append(d)

    logger.info(f"Detections affect {len(glb_groups)} unique GLB tiles.")

    # Prepare batches
    batch_tiles = []
    for glb_path, obstacles in glb_groups.items():
        # Derive patched GLB path
        # Original: data_out/{depth}/{last3}/{octant_path}.glb
        # Patched: street_cleanup/patches/{depth}/{last3}/{octant_path}.glb
        p = Path(glb_path)
        parts = p.parts
        # find where data_out is
        idx = parts.index("data_out")
        rel_parts = parts[idx + 1:]
        patched_path = PATCHES_DIR / Path(*rel_parts)
        
        batch_tiles.append({
            "glb_path": glb_path,
            "patched_glb_path": str(patched_path),
            "obstacles": obstacles,
        })

    batches = [batch_tiles[i:i + BLENDER_BATCH_SIZE] for i in range(0, len(batch_tiles), BLENDER_BATCH_SIZE)]
    logger.info(f"Divided work into {len(batches)} batches...")

    total_succeeded = 0
    total_failed = 0
    t_start = time.time()

    for idx, batch in enumerate(batches, start=1):
        success, fail = run_blender_batch(batch)
        total_succeeded += success
        total_failed += fail
        
        pct = (idx / len(batches)) * 100.0
        elapsed = time.time() - t_start
        eta = (elapsed / idx) * (len(batches) - idx) if idx > 0 else 0.0
        
        logger.info(
            f"Progress: {idx}/{len(batches)} batches ({pct:.1f}%) | "
            f"Succeeded: {total_succeeded}, Failed: {total_failed} | "
            f"Elapsed: {elapsed:.1f}s, ETA: {eta:.1f}s"
        )

    logger.info("=" * 60)
    logger.info("FLATTENING PROCESS COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Tiles successfully processed: {total_succeeded}")
    logger.info(f"Tiles failed: {total_failed}")
    logger.info(f"Total time: {time.time() - t_start:.1f}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
