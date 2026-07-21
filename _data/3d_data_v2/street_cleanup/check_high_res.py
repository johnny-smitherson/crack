import sys
from pathlib import Path
import json
import shapely.geometry
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from street_cleanup.coord_utils import latlon_to_enu, latlon_coords_to_enu
from street_cleanup.road_tiles import list_road_d20_tiles

def main():
    roads_geojson = Path("data_osm/roads.geojson")
    with open(roads_geojson, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    p_lines = []
    for f in data.get("features", []):
        if f.get("properties", {}).get("tags", {}).get("name") == "Șoseaua Pantelimon":
            geom = f["geometry"]
            if geom["type"] == "LineString":
                p_lines.append(shapely.geometry.LineString(latlon_coords_to_enu(geom["coordinates"])))
            elif geom["type"] == "MultiLineString":
                for line in geom["coordinates"]:
                    p_lines.append(shapely.geometry.LineString(latlon_coords_to_enu(line)))
                    
    road_union = unary_union(p_lines)
    tiles = list_road_d20_tiles(only_existing=True)
    
    print("Checking details for large tiles starting with 3043627270437:")
    count = 0
    for t in tiles:
        if t.octant_path.startswith("3043627270437"):
            east_min, north_min = latlon_to_enu(t.lat_south, t.lon_west)
            east_max, north_max = latlon_to_enu(t.lat_north, t.lon_east)
            tile_box = shapely.geometry.box(east_min, north_min, east_max, north_max)
            
            inter = road_union.intersection(tile_box)
            length = inter.length if not inter.is_empty else 0.0
            
            # Center distance to centerline
            east_c = (east_min + east_max) / 2.0
            north_c = (north_min + north_max) / 2.0
            pt = shapely.geometry.Point(east_c, north_c)
            dist = pt.distance(road_union)
            
            size_kb = t.glb_path.stat().st_size / 1024 if t.glb_path.exists() else 0.0
            print(f"Octant: {t.octant_path} | Length: {length:.1f}m | Dist: {dist:.1f}m | Size: {size_kb:.1f} KB")
            count += 1
            if count >= 30:
                break

if __name__ == "__main__":
    main()
