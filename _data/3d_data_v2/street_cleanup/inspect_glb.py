import trimesh
import sys
from pathlib import Path

GLB_PATH = Path("data_out/20/511/30436272704361607511.glb")

def main():
    if not GLB_PATH.exists():
        print(f"File not found: {GLB_PATH}")
        sys.exit(1)
        
    scene = trimesh.load(str(GLB_PATH))
    print(f"GLB scene loaded: {GLB_PATH}")
    print(f"Geometry names: {list(scene.geometry.keys())}")
    for name, geom in scene.geometry.items():
        print(f"Geometry '{name}': {len(geom.vertices)} vertices, {len(geom.faces)} faces")
        # Check if there is material/texture info
        if hasattr(geom, 'visual') and hasattr(geom.visual, 'material'):
            print(f"  Material: {geom.visual.material}")
            if hasattr(geom.visual.material, 'image'):
                print(f"  Texture: {geom.visual.material.image}")

if __name__ == "__main__":
    main()
