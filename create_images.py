#!/usr/bin/env python3
import os
import random
import subprocess
import shutil

BASE_DIR = "/data/duplicate-image-remover/photos"
os.makedirs(BASE_DIR, exist_ok=True)

for subdir in ["a", "b", "c"]:
    os.makedirs(os.path.join(BASE_DIR, subdir), exist_ok=True)

colors = ["red", "blue", "green", "yellow", "purple", "orange", "cyan", "magenta", "black", "white", "gray", "brown", "pink", "navy", "lime"]

def create_image(path, width, height, color, text):
    cmd = [
        "convert",
        "-size", f"{width}x{height}",
        f"xc:{color}",
        "-gravity", "center",
        "-pointsize", "24",
        "-annotate", "+0+0", text,
        path
    ]
    subprocess.run(cmd, capture_output=True)

unique_per_folder = 700
duplicate_per_folder = 300

for subdir in ["a", "b", "c"]:
    subdir_path = os.path.join(BASE_DIR, subdir)
    print(f"Creating {unique_per_folder} unique images in {subdir}...")
    for i in range(1, unique_per_folder + 1):
        width = random.choice([200, 300, 400, 500])
        height = random.choice([200, 300, 400, 500])
        color = random.choice(colors)
        text = f"{subdir.upper()}_{i:04d}"
        path = os.path.join(subdir_path, f"image_{i:04d}.jpg")
        create_image(path, width, height, color, text)
        if i % 100 == 0:
            print(f"  Created {i} unique images in {subdir}")

    print(f"Creating {duplicate_per_folder} duplicates in {subdir}...")
    source_indices = random.sample(range(1, unique_per_folder + 1), duplicate_per_folder)
    for i, src_idx in enumerate(source_indices):
        src_path = os.path.join(subdir_path, f"image_{src_idx:04d}.jpg")
        dup_path = os.path.join(subdir_path, f"dup_{i+1:04d}.jpg")
        shutil.copy2(src_path, dup_path)
        if (i + 1) % 100 == 0:
            print(f"  Created {i + 1} duplicates in {subdir}")

print("Done!")
print(f"Total: 3 folders x ({unique_per_folder} unique + {duplicate_per_folder} duplicates) = {3 * (unique_per_folder + duplicate_per_folder)} images")