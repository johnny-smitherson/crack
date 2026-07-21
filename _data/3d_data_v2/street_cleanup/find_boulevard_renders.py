import sys
from pathlib import Path
import json
import os
import shapely.geometry
from shapely.geometry import Point
from shapely.ops import unary_union
import subprocess
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from street_cleanup.coord_utils import latlon_to_enu, latlon_coords_to_enu
from street_cleanup.road_tiles import glb_path_for_octant
from street_cleanup.road_tiles import list_road_d20_tiles

# Paths
ONNX_PATH = Path("/home/vasile/.gemini/antigravity/scratch/crack/_slop/detection_sandbox/yolov7-m_itcvd_qgis.onnx")
OUTPUT_DIR = Path("/home/vasile/.gemini/antigravity/brain/923beaef-e863-4f20-b1bf-32bb66d46226/boulevards_v2")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_yolov7_onnx(image: np.ndarray, net, conf_threshold=0.20) -> list[dict]:
    h_img, w_img, _ = image.shape
    blob = cv2.dnn.blobFromImage(image, 1.0 / 255.0, (640, 640), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward()
    predictions = outputs[0]
    raw_detections = []
    for pred in predictions:
        obj_conf = pred[4]
        class_prob = pred[5]
        confidence = obj_conf * class_prob
        if confidence >= conf_threshold:
            x_c, y_c, w, h = pred[0:4]
            x_c = (x_c / 640.0) * w_img
            y_c = (y_c / 640.0) * h_img
            w = (w / 640.0) * w_img
            h = (h / 640.0) * h_img
            x1 = int(x_c - w / 2)
            y1 = int(y_c - h / 2)
            x2 = int(x_c + w / 2)
            y2 = int(y_c + h / 2)
            raw_detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": float(confidence)
            })
    # NMS
    boxes = [[d["bbox"][0], d["bbox"][1], d["bbox"][2]-d["bbox"][0], d["bbox"][3]-d["bbox"][1]] for d in raw_detections]
    scores = [d["confidence"] for d in raw_detections]
    indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.01, nms_threshold=0.4)
    if len(indices) > 0:
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()
        return [raw_detections[idx] for idx in indices]
    return []

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
    
    # List road tiles
    tiles = list_road_d20_tiles(only_existing=True)
    print(f"Total existing road tiles: {len(tiles)}")
    
    candidates = []
    for t in tiles:
        east_min, north_min = latlon_to_enu(t.lat_south, t.lon_west)
        east_max, north_max = latlon_to_enu(t.lat_north, t.lon_east)
        tile_box = shapely.geometry.box(east_min, north_min, east_max, north_max)
        
        inter = road_union.intersection(tile_box)
        length = inter.length if not inter.is_empty else 0.0
        
        size_kb = t.glb_path.stat().st_size / 1024 if t.glb_path.exists() else 0.0
        
        # We want tiles with a high centerline length inside them AND large file size (actual detailed boulevard geometry)
        if length > 40.0 and size_kb > 150:
            candidates.append((t, length, size_kb))
            
    # Sort candidates by size descending
    candidates.sort(key=lambda x: -x[2])
    
    print(f"Found {len(candidates)} candidates.")
    
    # Let's render the top 3 largest boulevard candidates
    spec_tiles = []
    for i, (t, length, size) in enumerate(candidates[:3], start=1):
        print(f"Candidate {i}: {t.octant_path} | Road length: {length:.1f}m | GLB size: {size:.1f} KB")
        glb_p = glb_path_for_octant(t.octant_path)
        spec_tiles.append({
            "octant_path": t.octant_path,
            "glb_path": str(glb_p),
            "jpg_path": str(OUTPUT_DIR / f"{t.octant_path}.jpg"),
            "meta_path": str(OUTPUT_DIR / f"{t.octant_path}.json"),
            "resolution": [1024, 1024],
            "ortho_scale_multiplier": 1.4 # Higher altitude / zoom out
        })
        
    spec = {"tiles": spec_tiles}
    batch_json_path = "/tmp/boulevards_v2_batch.json"
    with open(batch_json_path, "w") as f:
        json.dump(spec, f)
        
    print("Running Blender render...")
    cmd = ["blender", "-b", "-P", "street_cleanup/render_top_down.py", "--", batch_json_path]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("Blender failed:")
        print(proc.stderr)
        return
        
    print("Blender render complete.")
    
    print("Loading YOLOv7 model...")
    net = cv2.dnn.readNetFromONNX(str(ONNX_PATH))
    
    for tile in spec_tiles:
        jpg_path = Path(tile["jpg_path"])
        if not jpg_path.exists():
            print(f"Render failed for {tile['octant_path']}")
            continue
            
        img = cv2.imread(str(jpg_path))
        dets = run_yolov7_onnx(img, net, conf_threshold=0.15)
        print(f"Tile {tile['octant_path']}: detected {len(dets)} cars")
        
        annotated = img.copy()
        for d in dets:
            x1, y1, x2, y2 = d["bbox"]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(annotated, f"car {d['confidence']:.2f}", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
            
        out_path = OUTPUT_DIR / f"{tile['octant_path']}_detected.jpg"
        cv2.imwrite(str(out_path), annotated)
        print(f"Saved annotated image to {out_path}")

if __name__ == "__main__":
    main()
