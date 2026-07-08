"""
Sample camera viewpoints along OSM driveable roads for street-level rendering.

Processes the OSM roads, samples points every 20 meters, computes the direction
of travel (heading), and saves the viewpoints as a JSON list.

Output:
  - street_cleanup/camera_viewpoints.json

Run from _data/3d_data_v2/:
    uv run python street_cleanup/sample_camera_positions.py
"""

import json
import logging
import math
import sys
from pathlib import Path

from shapely.geometry import LineString
import shapely.wkb

from street_cleanup.coord_utils import latlon_to_enu

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("sample_camera_positions")

ROAD_POLYGON_WKB = Path("street_cleanup/road_polygons_enu.wkb")
ROADS_GEOJSON = Path("data_osm/roads.geojson")
OUTPUT_PATH = Path("street_cleanup/camera_viewpoints.json")

# Sample interval in meters
SAMPLE_INTERVAL = 20.0

# Driveable types we care about (from extract_streets.py)
DRIVEABLE_TYPES = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "residential", "living_street", "service", "unclassified",
}


def get_road_features():
    """Load and filter driveable road features from GeoJSON."""
    with open(ROADS_GEOJSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    features = []
    for feat in data.get("features", []):
        geom = feat.get("geometry", {})
        geom_type = geom.get("type", "")
        tags = feat.get("properties", {}).get("tags", {})
        highway = tags.get("highway", "")
        
        if geom_type in ("LineString", "MultiLineString") and highway in DRIVEABLE_TYPES:
            features.append(feat)
    return features


def main():
    logger.info("=" * 60)
    logger.info("Sampling street-level camera positions")
    logger.info("=" * 60)
    
    if not ROADS_GEOJSON.exists():
        logger.error(f"Roads GeoJSON not found: {ROADS_GEOJSON}")
        sys.exit(1)
        
    features = get_road_features()
    logger.info(f"Loaded {len(features)} driveable road features.")
    
    viewpoints = []
    viewpoint_id = 0
    
    for feat in features:
        geom = feat.get("geometry", {})
        geom_type = geom.get("type", "")
        coords = geom.get("coordinates", [])
        tags = feat.get("properties", {}).get("tags", {})
        road_name = tags.get("name", "Unnamed Road")
        highway = tags.get("highway", "unknown")
        
        # Convert coords to ENU
        linestrings = []
        if geom_type == "LineString":
            linestrings.append(LineString([latlon_to_enu(lat=c[1], lon=c[0]) for c in coords]))
        elif geom_type == "MultiLineString":
            for line_coords in coords:
                linestrings.append(LineString([latlon_to_enu(lat=c[1], lon=c[0]) for c in line_coords]))
                
        for ls in linestrings:
            length = ls.length
            if length < 5.0:
                continue
                
            # Number of samples along this line segment
            num_samples = max(1, int(length / SAMPLE_INTERVAL))
            
            for i in range(num_samples + 1):
                # Interpolate coordinate at distance along segment
                dist = min(length, i * SAMPLE_INTERVAL)
                pt = ls.interpolate(dist)
                
                # To get direction of road, look slightly ahead
                lookahead_dist = min(length, dist + 2.0)
                if lookahead_dist - dist < 0.5:
                    # If at the end, look slightly behind
                    lookahead_dist = dist
                    dist_prev = max(0.0, dist - 2.0)
                    pt_prev = ls.interpolate(dist_prev)
                    dx = pt.x - pt_prev.x
                    dy = pt.y - pt_prev.y
                else:
                    pt_next = ls.interpolate(lookahead_dist)
                    dx = pt_next.x - pt.x
                    dy = pt_next.y - pt.y
                    
                # Compute heading angle (in radians, CCW from East/X axis)
                heading_rad = math.atan2(dy, dx)
                heading_deg = math.degrees(heading_rad)
                
                viewpoints.append({
                    "id": viewpoint_id,
                    "road_name": road_name,
                    "highway": highway,
                    "east": round(pt.x, 2),
                    "north": round(pt.y, 2),
                    "heading_deg": round(heading_deg, 2),
                    "dx": round(dx, 4),
                    "dy": round(dy, 4),
                })
                viewpoint_id += 1
                
    logger.info(f"Sampled {len(viewpoints)} street-level viewpoints.")
    
    # Save to file
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(viewpoints, f, indent=2)
        
    logger.info(f"Saved viewpoints to {OUTPUT_PATH}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
