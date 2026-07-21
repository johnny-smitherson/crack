import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from street_cleanup.road_tiles import list_road_d20_tiles
import os

def main():
    tiles = list_road_d20_tiles(only_existing=True)
    print(f"Total existing road tiles: {len(tiles)}")
    
    # Sort tiles by GLB size descending
    tiles_with_size = []
    for t in tiles:
        if t.glb_path.exists():
            size = t.glb_path.stat().st_size
            tiles_with_size.append((t, size))
            
    tiles_with_size.sort(key=lambda x: -x[1])
    
    print("\nTop 15 largest road tiles:")
    for i, (t, size) in enumerate(tiles_with_size[:15], start=1):
        print(f"  {i}. {t.octant_path} | Size: {size/1024/1024:.2f} MB | GLB: {t.glb_path.name}")

if __name__ == "__main__":
    main()
