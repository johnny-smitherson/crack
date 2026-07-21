from huggingface_hub import hf_hub_download
import sys

try:
    print("Downloading VisDrone weights from Hugging Face...")
    weights_path = hf_hub_download(repo_id="dronefreak/visdrone-yolov8x", filename="best.pt")
    print(f"Success! Downloaded to: {weights_path}")
except Exception as e:
    print(f"Error downloading: {e}")
    sys.exit(1)
