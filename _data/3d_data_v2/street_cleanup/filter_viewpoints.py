"""
Filter sampled camera viewpoints to only those that lie within our high-detail tiles.

Matches each viewpoint (East, North) to the corresponding depth 20 tile (or depth 19 if no depth 20 is available).
Also limits the density of viewpoints (e.g., max 3 viewpoints per tile) to keep the render count reasonable.

Output:
  - street_cleanup/filtered_viewpoints.json

Run from _data/3d_data_v2/:
    uv run python street_cleanup/filter_viewpoints.py
"""

import json
import logging
import sys
from pathlib import Path

import pyarrow.parquet as pq

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("filter_viewpoints")

VIEWPOINTS_PATH = Path("street_cleanup/camera_viewpoints.json")
STREET_TILES_PATH = Path("street_cleanup/street_tiles.parquet")
OUTPUT_PATH = Path("street_cleanup/filtered_viewpoints.json")

# Maximum viewpoints per depth 20 tile to avoid redundant renders
MAX_VIEWPOINTS_PER_TILE = 3


def main():
    logger.info("=" * 60)
    logger.info("Filtering and optimizing camera viewpoints")
    logger.info("=" * 60)

    if not VIEWPOINTS_PATH.exists():
        logger.error(f"Viewpoints file not found: {VIEWPOINTS_PATH}")
        sys.exit(1)
    if not STREET_TILES_PATH.exists():
        logger.error(f"Street tiles file not found: {STREET_TILES_PATH}")
        sys.exit(1)

    # Load viewpoints
    with open(VIEWPOINTS_PATH, "r", encoding="utf-8") as f:
        viewpoints = json.load(f)
    logger.info(f"Loaded {len(viewpoints)} total viewpoints.")

    # Load street tiles
    table = pq.read_table(STREET_TILES_PATH)
    tiles = table.to_pylist()
    logger.info(f"Loaded {len(tiles)} street-intersecting tiles.")

    # Group tiles by depth for faster lookup
    tiles_d20 = [t for t in tiles if t["depth"] == 20]
    tiles_d19 = [t for t in tiles if t["depth"] == 19]
    logger.info(f"Depth 20 tiles: {len(tiles_d20)}, Depth 19 tiles: {len(tiles_d19)}")

    # For each viewpoint, find which tile it falls into (prefer depth 20, fallback to depth 19)
    matched_viewpoints = []
    tile_viewpoint_counts = {}

    for vp in viewpoints:
        ve = vp["east"]
        vn = vp["north"]

        # 1. Find depth 20 tile
        target_tile = None
        for t in tiles_d20:
            if t["east_min"] <= ve <= t["east_max"] and t["north_min"] <= vn <= t["north_max"]:
                target_tile = t
                break

        # 2. Fallback to depth 19 tile
        if not target_tile:
            for t in tiles_d19:
                if t["east_min"] <= ve <= t["east_max"] and t["north_min"] <= vn <= t["north_max"]:
                    target_tile = t
                    break

        if target_tile:
            tile_path = target_tile["octant_path"]
            
            # Check budget per tile
            count = tile_viewpoint_counts.get(tile_path, 0)
            if count < MAX_VIEWPOINTS_PER_TILE:
                tile_viewpoint_counts[tile_path] = count + 1
                
                # Append tile info to viewpoint
                vp_with_tile = vp.copy()
                vp_with_tile["octant_path"] = tile_path
                vp_with_tile["depth"] = target_tile["depth"]
                vp_with_tile["glb_path"] = target_tile["glb_path"]
                # Also include tile bounds (useful for mapping coordinates back)
                vp_with_tile["tile_bounds"] = {
                    "east_min": target_tile["east_min"],
                    "east_max": target_tile["east_max"],
                    "north_min": target_tile["north_min"],
                    "north_max": target_tile["north_max"],
                }
                matched_viewpoints.append(vp_with_tile)

    logger.info(f"Filtered to {len(matched_viewpoints)} viewpoints.")
    logger.info(f"Unique tiles covered: {len(tile_viewpoint_counts)}")

    # Save to file
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(matched_viewpoints, f, indent=2)

    logger.info(f"Saved optimized viewpoints to {OUTPUT_PATH}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
