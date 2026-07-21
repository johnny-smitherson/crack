import json
import shapely.geometry
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from street_cleanup.coord_utils import latlon_coords_to_enu, latlon_to_enu

ROADS_GEOJSON = Path("data_osm/roads.geojson")
NATURAL_GEOJSON = Path("data_osm/natural.geojson")

def load_road_polygon() -> shapely.geometry.MultiPolygon:
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
    # Buffer by 12.0 meters on each side to include sidewalks and roadside trees
    road_polygons = [line.buffer(12.0, cap_style="flat", join_style="mitre") for line in p_lines]
    return unary_union(road_polygons)

def main():
    if not NATURAL_GEOJSON.exists():
        print("natural.geojson not found")
        return
        
    road_poly = load_road_polygon()
    print("Loaded Șoseaua Pantelimon road polygon.")
    
    with open(NATURAL_GEOJSON, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    trees_in_road = 0
    total_trees = 0
    for feat in data.get("features", []):
        tags = feat.get("properties", {}).get("tags", {})
        if tags.get("natural") == "tree":
            total_trees += 1
            geom = feat.get("geometry", {})
            if geom.get("type") == "Point":
                lon, lat = geom["coordinates"]
                east, north = latlon_to_enu(lat, lon)
                pt = Point(east, north)
                if road_poly.contains(pt):
                    trees_in_road += 1
                    print(f"Tree on road found at: lat={lat}, lon={lon} (ENU: {east:.2f}, {north:.2f})")
                    
    print(f"Total trees in OSM natural.geojson: {total_trees}")
    print(f"Trees on Șoseaua Pantelimon road: {trees_in_road}")

if __name__ == "__main__":
    main()
