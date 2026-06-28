import os
import glob
import shutil
from pathlib import Path

OUTPUT_DIR = "data_out"

def main():
    # Find files matching data_out/<depth>/<file_id>.glb
    # which is data_out/*/*.glb
    old_pattern = os.path.join(OUTPUT_DIR, "*", "*.glb")
    glb_files = glob.glob(old_pattern)
    
    print(f"Found {len(glb_files)} files in old locations.")
    
    moved_count = 0
    for file_path in glb_files:
        p = Path(file_path)
        file_id = p.stem
        depth = p.parent.name
        
        # New directory: data_out/<depth>/<last_3_digits_of_file_id>
        last_three = file_id[-3:] if len(file_id) >= 3 else file_id
        new_dir = Path(OUTPUT_DIR) / depth / last_three
        new_path = new_dir / p.name
        
        new_dir.mkdir(parents=True, exist_ok=True)
        print(f"Moving {file_path} -> {new_path}")
        shutil.move(str(file_path), str(new_path))
        moved_count += 1
        
    print(f"Migration complete. Moved {moved_count} files.")

if __name__ == "__main__":
    main()
