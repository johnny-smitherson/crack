import json
import os
import subprocess
import cv2
import numpy as np
from pathlib import Path

# Paths
ONNX_PATH = Path("/home/vasile/.gemini/antigravity/scratch/crack/_slop/detection_sandbox/yolov7-m_itcvd_qgis.onnx")
OUTPUT_DIR = Path("/home/vasile/.gemini/antigravity/brain/923beaef-e863-4f20-b1bf-32bb66d46226/megamall")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TILE = {
    "octant_path": "30436272704370607412",
    "glb_path": "data_out/20/412/30436272704370607412.glb"
}

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
    print("Preparing render spec for Mega Mall tile...")
    spec_tiles = [{
        "octant_path": TILE["octant_path"],
        "glb_path": TILE["glb_path"],
        "jpg_path": str(OUTPUT_DIR / f"{TILE['octant_path']}.jpg"),
        "meta_path": str(OUTPUT_DIR / f"{TILE['octant_path']}.json"),
        "resolution": [1024, 1024]
    }]
        
    spec = {"tiles": spec_tiles}
    batch_json_path = "/tmp/megamall_batch.json"
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
    
    tile = spec_tiles[0]
    jpg_path = Path(tile["jpg_path"])
    if not jpg_path.exists():
        print(f"Render failed for {tile['octant_path']}")
        return
        
    img = cv2.imread(str(jpg_path))
    dets = run_yolov7_onnx(img, net, conf_threshold=0.20)
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
