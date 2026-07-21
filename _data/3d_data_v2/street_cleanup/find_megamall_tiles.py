import sys
from pathlib import Path
import json
import shapely.geometry
from shapely.geometry import Point
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from street_cleanup.coord_utils import latlon_to_enu
from street_cleanup.road_tiles import list_road_d20_tiles

# Mega Mall coordinates
MALL_LAT = 44.4427
MALL_LON = 26.1513
MALL_EAST, MALL_NORTH = latlon_to_enu(MALL_LAT, MALL_LON)

def main():
    tiles = list_road_d20_tiles(only_existing=True)
    print(f"Total existing road tiles: {len(tiles)}")
    
    nearby = []
    for t in tiles:
        # Convert south-west and north-east corners to ENU
        east_min, north_min = latlon_to_enu(t.lat_south, t.lon_west)
        east_max, north_max = latlon_to_enu(t.lat_north, t.lon_east)
        # Center of tile
        east_c = (east_min + east_max) / 2.0
        north_c = (north_min + north_max) / 2.0
        
        # Calculate distance to Mega Mall center
        dist = ((east_c - MALL_EAST)**2 + (north_c - MALL_NORTH)**2)**0.5
        if dist < 200.0:
            size_mb = t.glb_path.stat().st_size / 1024 / 1024 if t.glb_path.exists() else 0.0
            nearby.append((t, dist, size_mb))
            
    nearby.sort(key=lambda x: x[1])
    
    print("\nTiles near Mega Mall on Șoseaua Pantelimon:")
    for i, (t, dist, size_mb) in enumerate(nearby[:10], start=1):
        print(f"  {i}. {t.octant_path} | Distance: {dist:.1f}m | Size: {size_mb:.2f} MB | GLB: {t.glb_path.name}")

if __name__ == "__main__":
    main()
