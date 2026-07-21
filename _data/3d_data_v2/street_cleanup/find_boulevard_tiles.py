import sys
from pathlib import Path
import json
import shapely.geometry
from shapely.geometry import Point, box
from shapely.ops import unary_union
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from street_cleanup.coord_utils import latlon_to_enu, latlon_coords_to_enu
from street_cleanup.road_tiles import list_road_d20_tiles

def main():
    # Load road lines
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
    
    # List road tiles
    tiles = list_road_d20_tiles(only_existing=True)
    
    candidates = []
    for t in tiles:
        # Get bounding box
        east_min, north_min = latlon_to_enu(t.lat_south, t.lon_west)
        east_max, north_max = latlon_to_enu(t.lat_north, t.lon_east)
        tile_box = shapely.geometry.box(east_min, north_min, east_max, north_max)
        
        # Calculate intersection length of centerline with the tile
        inter = road_union.intersection(tile_box)
        length = inter.length if not inter.is_empty else 0.0
        
        # Center of tile
        east_c = (east_min + east_max) / 2.0
        north_c = (north_min + north_max) / 2.0
        pt = Point(east_c, north_c)
        dist_to_centerline = pt.distance(road_union)
        
        size_kb = t.glb_path.stat().st_size / 1024 if t.glb_path.exists() else 0.0
        
        # We want:
        # 1. High centerline intersection length (meaning the road runs straight through the tile)
        # 2. Distance to centerline very small (meaning the tile is centered on the road)
        # 3. GLB size > 200 KB (meaning there's actual geometry and not empty)
        # 4. Filter out tiles that are too close to Mega Mall building to avoid huge buildings
        if length > 50.0 and dist_to_centerline < 5.0 and size_kb > 200:
            candidates.append((t, length, dist_to_centerline, size_kb))
            
    # Sort candidates by distance to centerline ascending, then size descending
    candidates.sort(key=lambda x: (x[2], -x[3]))
    
    print("\nBest boulevard-centered road tiles:")
    for i, (t, length, dist, size) in enumerate(candidates[:10], start=1):
        print(f"  {i}. {t.octant_path} | Dist to Centerline: {dist:.2f}m | Road Length in Tile: {length:.1f}m | GLB Size: {size:.1f} KB")

if __name__ == "__main__":
    main()
