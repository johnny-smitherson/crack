import urllib.request
import sys
from pathlib import Path

URL = "https://chmura.put.poznan.pl/s/vgOeUN4H4tGsrGm/download"
DEST = Path("/home/vasile/.gemini/antigravity/scratch/crack/_data/3d_data_v2/street_cleanup/yolov7-m_itcvd_qgis.onnx")

def main():
    print(f"Downloading YOLOv7 ONNX weights from {URL}...")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(URL, str(DEST))
        print(f"Successfully downloaded to {DEST}")
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
