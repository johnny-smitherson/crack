#!/bin/bash

# Move to the script's directory
cd "$(dirname "$0")"

echo "Starting audio conversion and normalization..."

# Clean up previous folders/symlinks
if [ -L sound-fx2 ]; then
    echo "Removing symlink sound-fx2..."
    rm -f sound-fx2
fi

if [ -d sound-fx-normalized ]; then
    echo "Removing temporary sound-fx-normalized directory..."
    rm -rf sound-fx-normalized
fi

# Ensure sound-fx2 is a real directory
mkdir -p sound-fx2

# Find all mp3 or ogg files under sound-fx and process them
find sound-fx -type f \( -name "*.mp3" -o -name "*.ogg" \) | while read -r src_file; do
    # Strip leading "./" if any
    clean_path="${src_file#./}"
    # Get path relative to sound-fx
    rel_path="${clean_path#sound-fx/}"
    # Strip extension
    no_ext="${rel_path%.*}"
    # Target path under sound-fx2 with .mp3 extension
    dest_file="sound-fx2/${no_ext}.mp3"

    # Skip if the destination file already exists
    if [ -f "$dest_file" ]; then
        echo "Skipping $src_file (already normalized at $dest_file)"
        continue
    fi

    # Ensure the parent directory of the destination file exists
    mkdir -p "$(dirname "$dest_file")"

    echo "Normalizing and converting to MP3: $src_file -> $dest_file"

    # Query source sample rate using ffprobe
    sample_rate=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 "$src_file")

    if [ -z "$sample_rate" ]; then
        echo "Warning: Could not detect sample rate for $src_file. Defaulting to 44100."
        sample_rate=44100
    fi

    # Run ffmpeg with loudnorm (target loudness: -10 LUFS) preserving the original sample rate and saving as MP3
    ffmpeg -y -hide_banner -loglevel error -i "$src_file" -filter:a "loudnorm=I=-10:TP=-1.5:LRA=11" -ar "$sample_rate" "$dest_file"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to convert $src_file"
    fi
done

# Recreate the manifest listing all mp3 files under sound-fx2
echo "Recreating manifest at sound-fx2/manifest.txt..."
manifest_file="sound-fx2/manifest.txt"

# List all .mp3 files in sound-fx2, get paths relative to sound-fx2, sort and save
find sound-fx2 -type f -name "*.mp3" | while read -r mp3_file; do
    rel_path="${mp3_file#sound-fx2/}"
    echo "$rel_path"
done | sort > "$manifest_file"

echo "Audio conversion and manifest generation completed successfully."
