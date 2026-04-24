#!/usr/bin/env python3
"""Duplicate Image Remover - CLI tool to identify and remove duplicate images."""

import argparse
import hashlib
import os
import shutil
from pathlib import Path
from collections import defaultdict

try:
    import imagehash
    from PIL import Image
    PERCEPTUAL_AVAILABLE = True
except ImportError:
    PERCEPTUAL_AVAILABLE = False


SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}


def get_file_hash(filepath: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_perceptual_hash(filepath: Path):
    """Calculate perceptual hash of an image using pHash."""
    try:
        img = Image.open(filepath)
        return imagehash.phash(img)
    except Exception as e:
        print(f"Warning: Could not perceptual hash {filepath}: {e}")
        return None


def get_file_size(filepath: Path) -> int:
    """Get file size in bytes."""
    return filepath.stat().st_size


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def find_duplicates_in_dir(directory: Path, hash_type: str = 'sha256', threshold: int = 0) -> dict:
    """Find duplicate images within a single directory (non-recursive).
    
    Args:
        directory: Directory to scan
        hash_type: 'sha256' for exact hashing, 'perceptual' for perceptual hashing
        threshold: For perceptual hash, max hamming distance (0 = exact, 5-20 = similar)
    """
    hash_map = defaultdict(list)
    
    for filepath in sorted(directory.glob('*')):
        if filepath.is_file() and filepath.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                if hash_type == 'perceptual':
                    file_hash = get_perceptual_hash(filepath)
                    if file_hash is None:
                        continue
                else:
                    file_hash = get_file_hash(filepath)
                hash_map[file_hash].append(filepath)
            except (IOError, OSError) as e:
                print(f"Warning: Could not process {filepath}: {e}")
    
    if threshold == 0:
        return {h: files for h, files in hash_map.items() if len(files) > 1}
    
    duplicates = defaultdict(list)
    hashes = list(hash_map.items())
    for i, (hash1, files1) in enumerate(hashes):
        if hash1 is None:
            continue
        group = files1.copy()
        for hash2, files2 in hashes[i + 1:]:
            if hash2 is None:
                continue
            dist = hash1 - hash2
            if dist <= threshold:
                group.extend(files2)
        if len(group) > 1:
            key = f"sim_{str(hash1)[:16]}"
            duplicates[key] = list(set(group))
    
    return duplicates


def find_duplicates_per_subdir(base_dir: Path, hash_type: str = 'sha256', threshold: int = 0) -> dict:
    """Find duplicates in each immediate subdirectory."""
    duplicates_by_subdir = {}
    
    for subdir in sorted(base_dir.iterdir()):
        if subdir.is_dir():
            duplicates = find_duplicates_in_dir(subdir, hash_type, threshold)
            if duplicates:
                duplicates_by_subdir[subdir.name] = duplicates
                print(f"\n=== Processing: {subdir.name} ===")
                print_duplicates(duplicates)
    
    return duplicates_by_subdir


def print_duplicates(duplicates: dict) -> None:
    """Print duplicate groups."""
    if not duplicates:
        print("No duplicates found.")
        return
    
    total_duplicates = 0
    for file_hash, files in duplicates.items():
        hash_str = str(file_hash)[:16] if len(str(file_hash)) > 16 else str(file_hash)
        print(f"\nDuplicate group (hash: {hash_str}...):")
        total_duplicates += len(files) - 1
        for i, filepath in enumerate(files):
            size = get_file_size(filepath)
            status = "KEEP" if i == 0 else "DUPLICATE"
            print(f"  [{status}] {filepath} ({format_size(size)})")
    
    print(f"\nTotal duplicate files: {total_duplicates}")


def delete_duplicates(duplicates: dict) -> int:
    """Delete duplicate files, keeping the first occurrence."""
    deleted_count = 0
    for file_hash, files in duplicates.items():
        for filepath in files[1:]:
            try:
                filepath.unlink()
                print(f"Deleted: {filepath}")
                deleted_count += 1
            except (IOError, OSError) as e:
                print(f"Error deleting {filepath}: {e}")
    return deleted_count


def move_duplicates(duplicates: dict, directory: Path) -> int:
    """Move duplicate files to a 'duplicates' folder."""
    duplicates_dir = directory / 'duplicates'
    duplicates_dir.mkdir(exist_ok=True)
    
    moved_count = 0
    for file_hash, files in duplicates.items():
        for filepath in files[1:]:
            try:
                relative_path = filepath.relative_to(directory)
                subdir = relative_path.parts[0] if len(relative_path.parts) > 1 else ''
                
                if subdir:
                    dest_subdir = duplicates_dir / subdir
                    dest_subdir.mkdir(exist_ok=True)
                else:
                    dest_subdir = duplicates_dir
                
                dest = dest_subdir / filepath.name
                counter = 1
                while dest.exists():
                    stem = filepath.stem
                    suffix = filepath.suffix
                    dest = dest_subdir / f"{stem}_{counter}{suffix}"
                    counter += 1
                shutil.move(str(filepath), str(dest))
                print(f"Moved: {filepath} -> {dest}")
                moved_count += 1
            except (IOError, OSError) as e:
                print(f"Error moving {filepath}: {e}")
    return moved_count


def main():
    parser = argparse.ArgumentParser(
        description='Find and remove duplicate images from a directory.'
    )
    parser.add_argument(
        'directory',
        type=Path,
        help='Path to the directory containing images'
    )
    parser.add_argument(
        '--move',
        action='store_true',
        help='Move duplicates to a "duplicates" folder'
    )
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Permanently delete duplicates'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='Preview duplicates without taking action'
    )
    parser.add_argument(
        '--hash-type',
        choices=['sha256', 'perceptual'],
        default='sha256',
        help='Hash algorithm: sha256 (exact) or perceptual (similar, requires imagehash)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=0,
        help='Max hamming distance for perceptual hash (0=exact, 5-20=similar). Default: 0'
    )
    
    args = parser.parse_args()
    
    if args.hash_type == 'perceptual' and not PERCEPTUAL_AVAILABLE:
        print("Error: imagehash not installed. Run: pip install imagehash")
        return 1
    
    if args.threshold > 0 and args.hash_type != 'perceptual':
        print("Warning: --threshold only applies with --hash-type perceptual")
    
    if not args.directory.exists():
        print(f"Error: Directory '{args.directory}' does not exist.")
        return 1
    
    if not args.directory.is_dir():
        print(f"Error: '{args.directory}' is not a directory.")
        return 1
    
    print(f"Scanning directory: {args.directory}")
    duplicates_by_subdir = find_duplicates_per_subdir(args.directory, args.hash_type, args.threshold)
    
    if args.dry_run and not args.delete and not args.move:
        print("\nDry run mode - no changes made.")
        return 0
    
    total_deleted = 0
    total_moved = 0
    
    for subdir_name, duplicates in duplicates_by_subdir.items():
        subdir_path = args.directory / subdir_name
        
        if args.delete:
            count = delete_duplicates(duplicates)
            total_deleted += count
            print(f"Deleted {count} duplicate files in {subdir_name}.")
        
        if args.move:
            count = move_duplicates(duplicates, subdir_path)
            total_moved += count
            print(f"Moved {count} duplicate files in {subdir_name}.")
    
    if total_deleted > 0:
        print(f"\nTotal deleted: {total_deleted} duplicate files.")
    
    if total_moved > 0:
        print(f"\nTotal moved: {total_moved} duplicate files.")
    
    return 0


if __name__ == '__main__':
    exit(main())
