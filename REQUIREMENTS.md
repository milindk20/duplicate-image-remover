# Duplicate Image Remover - Requirements

## Project Overview

**Project Title:** Duplicate Image Remover  
**Project Type:** Python CLI Tool  
**Core Functionality:** A command-line tool that identifies and removes duplicate images from a directory using hash-based comparison.

## Features

1. **Hash-Based Detection**
   - Use SHA-256 hashing to detect exact duplicate files
   - Fast and efficient for large image collections

2. **CLI Interface**
   - Simple command-line interface
   - Support for specifying source directory
   - Preview mode to see duplicates before deletion
   - Interactive confirmation before removal

3. **Core Operations**
   - Scan directory for image files (jpg, jpeg, png, gif, bmp, webp)
   - Calculate hash for each image
   - Group duplicates by hash
   - Display duplicate groups with file paths and sizes
   - Remove duplicates (keep first occurrence)
   - Optional: Move duplicates to a separate folder instead of deleting

## Usage

```bash
python main.py <directory> [--move] [--delete] [--dry-run]
```

### Arguments
- `directory` - Path to the directory containing images
- `--move` - Move duplicates to a "duplicates" folder (optional)
- `--delete` - Permanently delete duplicates (optional)
- `--dry-run` - Preview duplicates without taking action (default)

### Example
```bash
python main.py ./photos --dry-run
python main.py ./photos --delete
python main.py ./photos --move
```

## Dependencies

- Python 3.7+
- Standard library only (hashlib, os, pathlib, argparse)
- For perceptual hashing: `pip install imagehash pillow`

### Hash Types

1. **SHA-256 (default)**: Exact byte-level matching
   ```bash
   python main.py ./photos --hash-type sha256
   ```

2. **Perceptual (pHash)**: Similar images despite minor changes
   ```bash
   pip install imagehash pillow
   python main.py ./photos --hash-type perceptual --threshold 10
   ```
   - `--threshold`: 0 = identical, 5-10 = very similar, 15-20 = loose matching