#!/usr/bin/env python3
"""declutter.py — sort a messy folder into subfolders by file type.

Standard library only. Defaults to a safe dry run; pass --apply to move files.

Examples:
    python3 declutter.py                 # dry-run on the current directory
    python3 declutter.py --path ~/Downloads
    python3 declutter.py --path ~/Downloads --apply
"""
import argparse
import json
import os
import shutil
import sys
import time

LOG_NAME = ".declutter_log.json"


def unique_dest(dest_dir, name):
    """Return a path in dest_dir that won't overwrite an existing file."""
    dest = os.path.join(dest_dir, name)
    if not os.path.exists(dest):
        return dest
    stem, ext = os.path.splitext(name)
    i = 1
    while True:
        candidate = os.path.join(dest_dir, f"{stem} ({i}){ext}")
        if not os.path.exists(candidate):
            return candidate
        i += 1

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
    p.add_argument("--older-than-days", type=int, default=0, metavar="N",
                   help="Only move files last modified more than N days ago.")
    p.add_argument("--undo", action="store_true",
                   help="Reverse the moves from the last --apply run in this folder.")
    return p


def gather(folder, older_than_days=0):
    """Return list of (filename, category) for regular files in folder."""
    items = []
    category_names = set(CATEGORIES) | {OTHER}
    cutoff = time.time() - older_than_days * 86400 if older_than_days > 0 else None
    for name in sorted(os.listdir(folder)):
        full = os.path.join(folder, name)
        if not os.path.isfile(full):
            continue
        if name.startswith("."):
            continue  # leave hidden files alone
        # don't re-sort a category folder that happens to be a file name match
        if name in category_names:
            continue
        if cutoff is not None and os.path.getmtime(full) > cutoff:
            continue  # too recent — leave it alone
        items.append((name, category_for(name)))
    return items


def run(args):
    folder = os.path.abspath(os.path.expanduser(args.path))
    if not os.path.isdir(folder):
        print(f"Error: {folder} is not a directory.", file=sys.stderr)
        return 1

    if args.undo:
        return undo(folder)

    items = gather(folder, args.older_than_days)
    if not items:
        note = f" older than {args.older_than_days} days" if args.older_than_days > 0 else ""
        print(f"Nothing to sort — no loose files{note} found.")
        return 0

    mode = "MOVING" if args.apply else "DRY RUN (nothing moved; use --apply)"
    age = f", only files older than {args.older_than_days} days" if args.older_than_days > 0 else ""
    print(f"{mode} in {folder}{age}\n")

    counts = {}
    moves = []  # (src, dest) for the undo log
    for name, cat in items:
        counts[cat] = counts.get(cat, 0) + 1
        dest_dir = os.path.join(folder, cat)
        src = os.path.join(folder, name)
        if args.apply:
            os.makedirs(dest_dir, exist_ok=True)
            dest = unique_dest(dest_dir, name)
            shutil.move(src, dest)
            moves.append((src, dest))
            renamed = " (renamed to avoid collision)" if os.path.basename(dest) != name else ""
            print(f"  {name} -> {cat}/{os.path.basename(dest)}{renamed}")
        else:
            print(f"  {name} -> {cat}/")

    if args.apply and moves:
        with open(os.path.join(folder, LOG_NAME), "w") as f:
            json.dump({"moves": moves}, f, indent=2)

    print("\nSummary:")
    for cat in sorted(counts):
        print(f"  {cat:12} {counts[cat]}")
    print(f"  {'TOTAL':12} {sum(counts.values())}")
    if args.apply:
        print("\nRun with --undo to reverse this.")
    return 0


def undo(folder):
    log_path = os.path.join(folder, LOG_NAME)
    if not os.path.exists(log_path):
        print("No previous run to undo (no log found).")
        return 1
    with open(log_path) as f:
        moves = json.load(f).get("moves", [])
    restored = 0
    for src, dest in reversed(moves):
        if not os.path.exists(dest):
            print(f"  skip (missing): {dest}")
            continue
        target = unique_dest(os.path.dirname(src), os.path.basename(src))
        shutil.move(dest, target)
        restored += 1
        print(f"  {os.path.relpath(dest, folder)} -> {os.path.relpath(target, folder)}")
    os.remove(log_path)
    print(f"\nRestored {restored} file(s).")
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
