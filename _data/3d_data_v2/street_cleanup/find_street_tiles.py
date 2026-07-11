"""
Find which map tiles (from manifest.parquet) intersect with street areas.

Loads the merged road polygon from extract_streets.py and the tile manifest,
then performs spatial intersection tests to identify tiles that overlap streets.

Only high-detail tiles (depth >= 18) are selected, as lower LODs are too coarse
for meaningful obstacle detection.

Output:
  - street_cleanup/street_tiles.parquet

Run from _data/3d_data_v2/:
    uv run python street_cleanup/find_street_tiles.py
"""

import logging
import sys
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from shapely.geometry import box as shapely_box
import shapely.wkb

from street_cleanup.coord_utils import latlon_to_enu

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("find_street_tiles")

# Paths
MANIFEST_PATH = Path("data_out/manifest.parquet")
ROAD_POLYGON_WKB = Path("street_cleanup/road_polygons_enu.wkb")
OUTPUT_PATH = Path("street_cleanup/street_tiles.parquet")

# Only consider tiles at this depth or higher (more detailed)
MIN_DEPTH = 18


def main():
    logger.info("=" * 60)
    logger.info("Finding tiles that intersect streets")
    logger.info("=" * 60)

    # Load road polygon
    if not ROAD_POLYGON_WKB.exists():
        logger.error(f"Road polygon not found: {ROAD_POLYGON_WKB}")
        logger.error("Run extract_streets.py first!")
        sys.exit(1)

    logger.info(f"Loading road polygon from {ROAD_POLYGON_WKB}...")
    t0 = time.time()
    with open(ROAD_POLYGON_WKB, "rb") as f:
        road_polygon = shapely.wkb.loads(f.read())
    logger.info(f"Road polygon loaded in {time.time() - t0:.1f}s (area={road_polygon.area:.0f} m²)")

    # Prepare the road polygon for faster intersection tests (in Shapely 2.x this is done in-place via shapely.prepare)
    shapely.prepare(road_polygon)

    # Load manifest
    if not MANIFEST_PATH.exists():
        logger.error(f"Manifest not found: {MANIFEST_PATH}")
        sys.exit(1)

    logger.info(f"Loading manifest from {MANIFEST_PATH}...")
    table = pq.read_table(MANIFEST_PATH)
    total_tiles = table.num_rows
    logger.info(f"Loaded {total_tiles} tiles")

    # Convert to list of dicts for processing
    rows = table.to_pylist()

    # Filter and test intersection
    street_tiles = []
    depth_stats: dict[int, dict[str, int]] = {}
    skipped_low_depth = 0

    logger.info(f"Testing tile-road intersections (min_depth={MIN_DEPTH})...")
    t0 = time.time()

    for i, row in enumerate(rows):
        depth = row["depth"]

        # Skip low-detail tiles
        if depth < MIN_DEPTH:
            skipped_low_depth += 1
            continue

        # Initialize depth stats
        if depth not in depth_stats:
            depth_stats[depth] = {"total": 0, "intersecting": 0}
        depth_stats[depth]["total"] += 1

        # Convert geographic lat/lon from manifest to ENU coordinates
        east_min, north_min = latlon_to_enu(row["lat_south"], row["lon_west"])
        east_max, north_max = latlon_to_enu(row["lat_north"], row["lon_east"])

        # Create 2D bounding box in ENU (ignore height)
        tile_box = shapely_box(
            east_min, north_min,
            east_max, north_max,
        )

        # Test intersection with road polygon
        if road_polygon.intersects(tile_box):
            # Compute road coverage ratio
            try:
                intersection = road_polygon.intersection(tile_box)
                coverage = intersection.area / tile_box.area if tile_box.area > 0 else 0.0
            except Exception:
                coverage = 0.0

            street_tiles.append({
                "octant_path": row["octant_path"],
                "depth": depth,
                "glb_path": row["glb_path"],
                "east_min": east_min,
                "east_max": east_max,
                "north_min": north_min,
                "north_max": north_max,
                "up_min": row["y_min"],
                "up_max": row["y_max"],
                "road_coverage_ratio": round(coverage, 4),
                "vertex_count": row["vertex_count"],
                "triangle_count": row["triangle_count"],
            })
            depth_stats[depth]["intersecting"] += 1

        # Progress
        if (i + 1) % 1000 == 0:
            logger.info(f"  Processed {i + 1}/{total_tiles} tiles...")

    elapsed = time.time() - t0
    logger.info(f"Intersection testing complete in {elapsed:.1f}s")

    # Save results
    if street_tiles:
        out_table = pa.Table.from_pylist(street_tiles)
        pq.write_table(out_table, OUTPUT_PATH)
        logger.info(f"Saved {len(street_tiles)} street tiles to {OUTPUT_PATH}")
    else:
        logger.warning("No street-intersecting tiles found!")

    # Print summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total tiles in manifest: {total_tiles}")
    logger.info(f"Skipped (depth < {MIN_DEPTH}): {skipped_low_depth}")
    logger.info(f"Tiles intersecting streets: {len(street_tiles)}")
    logger.info("")
    logger.info("By depth:")
    for depth in sorted(depth_stats.keys()):
        stats = depth_stats[depth]
        logger.info(
            f"  Depth {depth}: {stats['intersecting']}/{stats['total']} "
            f"({100 * stats['intersecting'] / max(stats['total'], 1):.0f}%)"
        )

    if street_tiles:
        # Coverage stats
        coverages = [t["road_coverage_ratio"] for t in street_tiles]
        avg_coverage = sum(coverages) / len(coverages)
        logger.info("")
        logger.info(f"Average road coverage per tile: {avg_coverage:.1%}")
        high_coverage = sum(1 for c in coverages if c > 0.3)
        logger.info(f"Tiles with >30% road coverage: {high_coverage}")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
