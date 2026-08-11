#!/usr/bin/env python3
"""declutter.py — sort a messy folder into subfolders by file type.

Standard library only. Defaults to a safe dry run; pass --apply to move files.

Examples:
    python3 declutter.py                 # dry-run on the current directory
    python3 declutter.py --path ~/Downloads
    python3 declutter.py --path ~/Downloads --apply
"""
import argparse
import os
import shutil
import sys

# extension -> category
CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic", ".tiff"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".pages"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods", ".numbers"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Archives": {".zip", ".tar", ".gz", ".rar", ".7z", ".bz2", ".xz"},
}
OTHER = "Other"


def category_for(filename):
    ext = os.path.splitext(filename)[1].lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return OTHER


def build_parser():
    p = argparse.ArgumentParser(description="Sort files in a folder into subfolders by type.")
    p.add_argument("--path", default=".", help="Folder to declutter (default: current directory).")
    p.add_argument("--apply", action="store_true",
                   help="Actually move files. Without this, runs as a dry run.")
    return p


def gather(folder):
    """Return list of (filename, category) for regular files in folder."""
    items = []
    category_names = set(CATEGORIES) | {OTHER}
    for name in sorted(os.listdir(folder)):
        full = os.path.join(folder, name)
        if not os.path.isfile(full):
            continue
        if name.startswith("."):
            continue  # leave hidden files alone
        # don't re-sort a category folder that happens to be a file name match
        if name in category_names:
            continue
        items.append((name, category_for(name)))
    return items


def run(args):
    folder = os.path.abspath(os.path.expanduser(args.path))
    if not os.path.isdir(folder):
        print(f"Error: {folder} is not a directory.", file=sys.stderr)
        return 1

    items = gather(folder)
    if not items:
        print("Nothing to sort — no loose files found.")
        return 0

    mode = "MOVING" if args.apply else "DRY RUN (nothing moved; use --apply)"
    print(f"{mode} in {folder}\n")

    counts = {}
    for name, cat in items:
        counts[cat] = counts.get(cat, 0) + 1
        dest_dir = os.path.join(folder, cat)
        arrow = "->"
        if args.apply:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(os.path.join(folder, name), os.path.join(dest_dir, name))
        print(f"  {name} {arrow} {cat}/")

    print("\nSummary:")
    for cat in sorted(counts):
        print(f"  {cat:12} {counts[cat]}")
    print(f"  {'TOTAL':12} {sum(counts.values())}")
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
