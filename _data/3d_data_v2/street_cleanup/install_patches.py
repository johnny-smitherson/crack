"""
Installs patched GLB tiles, replacing the original ones.

Creates backups of the original tiles (.glb.bak) before replacing them,
and supports dry-run mode and rollback of all changes.

After installing patches, runs rebuild_manifest.py to update manifest.parquet.

Run from _data/3d_data_v2/:
    # Preview changes
    uv run python street_cleanup/install_patches.py --dry-run
    # Install changes
    uv run python street_cleanup/install_patches.py
    # Rollback changes (if needed)
    uv run python street_cleanup/install_patches.py --rollback
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("install_patches")

PATCHES_DIR = Path("street_cleanup/patches")
DATA_OUT_DIR = Path("data_out")


def rollback():
    """Restore all backups (.glb.bak) to their original locations."""
    logger.info("=" * 60)
    logger.info("Rolling back patched tiles...")
    logger.info("=" * 60)
    
    restored = 0
    errors = 0
    
    # Walk data_out to find all .glb.bak files
    for root, dirs, files in os.walk(DATA_OUT_DIR):
        for f in files:
            if f.endswith(".glb.bak"):
                bak_path = Path(root) / f
                orig_path = Path(root) / f.replace(".glb.bak", ".glb")
                
                try:
                    logger.info(f"Restoring backup: {orig_path.name}")
                    # Overwrite patched GLB with backup
                    shutil.copy2(bak_path, orig_path)
                    # Delete backup
                    os.remove(bak_path)
                    restored += 1
                except Exception as e:
                    logger.error(f"Failed to restore {orig_path.name}: {e}")
                    errors += 1
                    
    logger.info("=" * 60)
    logger.info(f"Rollback complete: {restored} files restored, {errors} errors.")
    logger.info("=" * 60)
    
    if restored > 0:
        logger.info("Rebuilding manifest...")
        subprocess.run(["python", "rebuild_manifest.py"])


def main():
    parser = argparse.ArgumentParser(description="Install or rollback patched map tiles.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying files")
    parser.add_argument("--rollback", action="store_true", help="Restore original tiles from backup (.glb.bak)")
    args = parser.parse_args()

    if args.rollback:
        rollback()
        sys.exit(0)

    logger.info("=" * 60)
    logger.info("Installing patched GLB tiles")
    logger.info("=" * 60)

    if not PATCHES_DIR.exists():
        logger.error(f"Patches directory not found: {PATCHES_DIR}")
        sys.exit(1)

    # Find all patched GLB files
    patches = []
    for root, dirs, files in os.walk(PATCHES_DIR):
        for f in files:
            if f.endswith(".glb"):
                p_path = Path(root) / f
                # Get path relative to street_cleanup/patches
                rel_path = p_path.relative_to(PATCHES_DIR)
                orig_path = DATA_OUT_DIR / rel_path
                patches.append((p_path, orig_path))

    logger.info(f"Found {len(patches)} patched tiles to install.")
    if not patches:
        logger.warning("No patched tiles found to install!")
        sys.exit(0)

    installed = 0
    errors = 0

    for patch_path, orig_path in patches:
        if not orig_path.exists():
            logger.warning(f"Original file not found for patch: {orig_path.name} (skipping)")
            continue
            
        bak_path = orig_path.with_suffix(".glb.bak")
        
        if args.dry_run:
            logger.info(f"[DRY-RUN] Install patch {patch_path.name} to {orig_path}")
            if not bak_path.exists():
                logger.info(f"[DRY-RUN] Create backup: {bak_path}")
            installed += 1
        else:
            try:
                # 1. Create backup if it doesn't exist yet
                if not bak_path.exists():
                    logger.info(f"Backing up {orig_path.name} -> {bak_path.name}")
                    shutil.copy2(orig_path, bak_path)
                else:
                    logger.info(f"Backup already exists for {orig_path.name}")
                    
                # 2. Copy patch to overwrite original
                logger.info(f"Overwriting original: {orig_path.name}")
                shutil.copy2(patch_path, orig_path)
                installed += 1
            except Exception as e:
                logger.error(f"Failed to install patch for {orig_path.name}: {e}")
                errors += 1

    logger.info("=" * 60)
    logger.info(f"Install process completed ({'DRY-RUN' if args.dry_run else 'ACTIVE'})")
    logger.info(f"Successfully processed: {installed}/{len(patches)}")
    logger.info(f"Errors: {errors}")
    logger.info("=" * 60)

    if not args.dry_run and installed > 0:
        logger.info("Rebuilding manifest.parquet...")
        subprocess.run(["python", "rebuild_manifest.py"])
        logger.info("Manifest rebuild complete!")


if __name__ == "__main__":
    main()
