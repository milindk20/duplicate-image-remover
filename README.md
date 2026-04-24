# Duplicate Image Remover

A Python CLI tool that identifies and removes duplicate images from a directory using hash-based comparison.

## Features

- **Two Hash Types:**
  - SHA-256: Exact byte-level matching
  - Perceptual (pHash): Similar images despite minor changes
- Supports JPG, JPEG, PNG, GIF, BMP, WebP
- Preview mode (dry-run)
- Delete duplicates or move to a folder
- Processes each subdirectory independently

## Usage

```bash
python main.py <directory> [--dry-run] [--delete] [--move] [--hash-type TYPE] [--threshold N]
```

### Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview duplicates without taking action (default) |
| `--delete` | Permanently delete duplicates |
| `--move` | Move duplicates to a "duplicates" folder |
| `--hash-type` | Hash algorithm: `sha256` (exact) or `perceptual` (similar) |
| `--threshold` | Max hamming distance for perceptual hash (0=identical, 5-20=similar) |

### Hash Type Comparison

| Hash Type | Use Case | Threshold |
|-----------|---------|-----------|
| `sha256` | Exact duplicate files | Not applicable |
| `perceptual` | Similar images (resized, compressed) | 0 (exact) to 20 (loose) |

### Threshold Guide

| Threshold | Description | Best For |
|-----------|-------------|----------|
| 0 | Identical images | Exactly the same file |
| 1-5 | Very similar | Minor compression differences |
| 6-10 | Similar | Resized versions |
| 11-20 | Loose match | Heavily modified images |

### Test Results

Perceptual hash detects more duplicates as threshold increases:

| Threshold | A | b | c | d | Total |
|-----------|---|---|---|---|-------|
| 0 | 2 | 2 | 2 | 2 | 8 |
| 1 | 2 | 2 | 2 | 2 | 8 |
| 2 | 2 | 2 | 2 | 2 | 8 |
| 3 | 2 | 2 | 2 | 2 | 8 |
| 4 | 2 | 2 | 2 | 2 | 8 |
| 5 | 2 | 2 | 2 | 2 | 8 |
| 10 | 3 | 3 | 3 | 3 | 12 |
| 15 | 3 | 3 | 3 | 3 | 12 |
| 20 | 3 | 3 | 3 | 3 | 12 |

**SHA-256:** 2 per folder = **8 total** (same as perceptual threshold 0-5)

### Examples

```bash
# SHA-256 (exact duplicates) - default
python main.py ./photos --delete

# Perceptual hash - similar images
pip install imagehash pillow
python main.py ./photos --hash-type perceptual --threshold 5 --delete

# Preview duplicates
python main.py ./photos --dry-run

# Move duplicates to folder
python main.py ./photos --move
```

### Directory Structure

The tool processes each immediate subdirectory independently:

```
photos/
├── A/
│   ├── image1.jpg
│   └── image2.jpg  (duplicate within A)
├── b/
│   ├── image1.jpg
│   └── image2.jpg
└── c/
```

Duplicates are only detected **within** each folder, not across folders.

## Requirements

- Python 3.7+
- Standard library (for SHA-256)
- For perceptual hashing: `pip install imagehash pillow`

### Installation

```bash
# Basic (SHA-256 only) - no install needed
pip install -r requirements.txt

# With perceptual hashing
pip install imagehash pillow
```