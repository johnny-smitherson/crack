"""
Extract driveable streets from OSM roads GeoJSON and create buffered road polygons.

Reads data_osm/roads.geojson, filters to driveable road types, converts coordinates
to local ENU meters, buffers each road by its estimated width, and merges all road
polygons into a single MultiPolygon.

Output:
  - street_cleanup/road_polygons_enu.wkb  (binary, for fast loading)
  - street_cleanup/road_polygons_meta.json (metadata + stats)

Run from _data/3d_data_v2/:
    uv run python street_cleanup/extract_streets.py
"""

import json
import logging
import sys
import time
from pathlib import Path

from shapely.geometry import LineString, MultiLineString, shape, mapping
from shapely.ops import unary_union
import shapely.wkb

from street_cleanup.coord_utils import latlon_to_enu, latlon_coords_to_enu

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("extract_streets")

# Input / output paths
ROADS_GEOJSON = Path("data_osm/roads.geojson")
OUTPUT_WKB = Path("street_cleanup/road_polygons_enu.wkb")
OUTPUT_META = Path("street_cleanup/road_polygons_meta.json")

# Driveable highway types
DRIVEABLE_TYPES = {
    "motorway", "trunk",
    "primary", "secondary", "tertiary",
    "residential", "living_street",
    "service", "unclassified", "construction",
    "motorway_link", "trunk_link",
    "primary_link", "secondary_link", "tertiary_link",
}

# Non-driveable types to explicitly skip
SKIP_TYPES = {
    "footway", "crossing", "steps", "pedestrian", "path",
    "cycleway", "track", "bus_stop", "traffic_signals",
    "street_lamp", "give_way", "elevator", "proposed",
}

# Road width estimates in meters based on highway type
ROAD_WIDTHS = {
    "motorway": 12.0,
    "trunk": 12.0,
    "primary": 10.0,
    "secondary": 8.0,
    "tertiary": 7.0,
    "residential": 6.0,
    "living_street": 6.0,
    "service": 4.0,
    "unclassified": 5.0,
    "construction": 6.0,
    "motorway_link": 4.0,
    "trunk_link": 4.0,
    "primary_link": 4.0,
    "secondary_link": 4.0,
    "tertiary_link": 4.0,
}
DEFAULT_WIDTH = 6.0


def get_road_width(tags: dict) -> float:
    """Determine road width from OSM tags."""
    # If explicit lane count is given, use it
    lanes = tags.get("lanes")
    if lanes is not None:
        try:
            return int(lanes) * 3.5
        except (ValueError, TypeError):
            pass

    # Fall back to highway type lookup
    highway = tags.get("highway", "")
    return ROAD_WIDTHS.get(highway, DEFAULT_WIDTH)


def extract_linestrings_enu(geometry: dict) -> list[LineString]:
    """
    Extract LineString geometries from a GeoJSON geometry and convert to ENU.

    Handles LineString and MultiLineString types. Returns empty list for
    Point and other non-line geometries.
    """
    geom_type = geometry.get("type", "")
    coords = geometry.get("coordinates", [])
    results = []

    if geom_type == "LineString":
        enu_coords = latlon_coords_to_enu(coords)
        if len(enu_coords) >= 2:
            results.append(LineString(enu_coords))

    elif geom_type == "MultiLineString":
        for line_coords in coords:
            enu_coords = latlon_coords_to_enu(line_coords)
            if len(enu_coords) >= 2:
                results.append(LineString(enu_coords))

    # Skip Point, Polygon, etc.
    return results


def main():
    logger.info("=" * 60)
    logger.info("Street Extraction from OSM Roads")
    logger.info("=" * 60)

    # Load GeoJSON
    if not ROADS_GEOJSON.exists():
        logger.error(f"Roads GeoJSON not found: {ROADS_GEOJSON}")
        sys.exit(1)

    logger.info(f"Loading {ROADS_GEOJSON}...")
    t0 = time.time()
    with open(ROADS_GEOJSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features", [])
    logger.info(f"Loaded {len(features)} features in {time.time() - t0:.1f}s")

    # Process features
    accepted = 0
    rejected = 0
    skipped_point = 0
    skipped_type = 0
    total_segments = 0
    total_length_m = 0.0

    road_polygons = []
    highway_type_counts: dict[str, int] = {}

    for feat in features:
        geom = feat.get("geometry", {})
        geom_type = geom.get("type", "")
        tags = feat.get("properties", {}).get("tags", {})
        highway = tags.get("highway", "")

        # Skip point features (traffic signals, bus stops, etc.)
        if geom_type == "Point":
            skipped_point += 1
            rejected += 1
            continue

        # Check if highway type is driveable
        if highway not in DRIVEABLE_TYPES:
            skipped_type += 1
            rejected += 1
            continue

        # Extract LineString geometries and convert to ENU
        linestrings = extract_linestrings_enu(geom)
        if not linestrings:
            rejected += 1
            continue

        accepted += 1
        highway_type_counts[highway] = highway_type_counts.get(highway, 0) + 1

        # Buffer each linestring by road width
        width = get_road_width(tags)
        half_width = width / 2.0

        for ls in linestrings:
            total_segments += 1
            total_length_m += ls.length

            try:
                # Add 1.5 meters to half_width to include sidewalks and curbs (Q1)
                buffered = ls.buffer(half_width + 1.5, cap_style="flat", join_style="mitre")
                if buffered.is_valid and not buffered.is_empty:
                    road_polygons.append(buffered)
            except Exception as e:
                logger.warning(f"Buffer failed for segment: {e}")

    logger.info(f"Accepted: {accepted}, Rejected: {rejected}")
    logger.info(f"  Skipped (Point geometry): {skipped_point}")
    logger.info(f"  Skipped (non-driveable type): {skipped_type}")
    logger.info(f"Highway type breakdown:")
    for hw, count in sorted(highway_type_counts.items(), key=lambda x: -x[1]):
        logger.info(f"  {hw}: {count}")

    # Merge all road polygons
    logger.info(f"Merging {len(road_polygons)} road polygons...")
    t0 = time.time()
    merged = unary_union(road_polygons)
    merge_time = time.time() - t0
    logger.info(f"Merge complete in {merge_time:.1f}s")

    # Calculate stats
    total_area_m2 = merged.area
    total_length_km = total_length_m / 1000.0
    bounds = merged.bounds  # (min_east, min_north, max_east, max_north)

    logger.info(f"Total road segments: {total_segments}")
    logger.info(f"Total road length: {total_length_km:.1f} km")
    logger.info(f"Total road surface area: {total_area_m2:.0f} m² ({total_area_m2 / 10000:.2f} ha)")
    logger.info(f"Bounds (ENU): E[{bounds[0]:.1f}, {bounds[2]:.1f}], N[{bounds[1]:.1f}, {bounds[3]:.1f}]")

    # Save WKB (binary, fast loading)
    logger.info(f"Saving road polygons to {OUTPUT_WKB}...")
    with open(OUTPUT_WKB, "wb") as f:
        f.write(shapely.wkb.dumps(merged))

    # Save metadata
    meta = {
        "total_features": len(features),
        "accepted_features": accepted,
        "rejected_features": rejected,
        "total_segments": total_segments,
        "total_length_km": round(total_length_km, 2),
        "total_area_m2": round(total_area_m2, 1),
        "bounds_enu": {
            "east_min": round(bounds[0], 2),
            "north_min": round(bounds[1], 2),
            "east_max": round(bounds[2], 2),
            "north_max": round(bounds[3], 2),
        },
        "highway_type_counts": highway_type_counts,
        "road_widths_used": ROAD_WIDTHS,
    }
    with open(OUTPUT_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    logger.info(f"Saved metadata to {OUTPUT_META}")
    logger.info("=" * 60)
    logger.info("Street extraction complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
