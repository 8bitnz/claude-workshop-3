#!/usr/bin/env python3
"""find_dupes.py — find duplicate files by content (standard library only).

Walks a folder recursively, groups files with identical content using an MD5
hash (read in chunks so large files are fine), and reports the duplicate groups
and how much space could be reclaimed. This version only reports — it never
deletes anything.

Usage:
    python3 find_dupes.py /path/to/folder
"""
import argparse
import hashlib
import os
import sys

CHUNK = 65536  # 64 KB


def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(root):
    """Return {hash: [paths]} for groups with more than one file."""
    by_size = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            path = os.path.join(dirpath, name)
            try:
                size = os.path.getsize(path)
            except OSError:
                continue
            by_size.setdefault(size, []).append(path)

    # Only hash files whose size collides — cheap pre-filter.
    by_hash = {}
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        for path in paths:
            try:
                by_hash.setdefault(file_hash(path), []).append(path)
            except OSError:
                continue
    return {h: p for h, p in by_hash.items() if len(p) > 1}


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def report(groups):
    if not groups:
        print("No duplicate files found. 🎉")
        return
    reclaimable = 0
    print(f"Found {len(groups)} group(s) of duplicates:\n")
    for i, (h, paths) in enumerate(sorted(groups.items(), key=lambda kv: -os.path.getsize(kv[1][0])), 1):
        size = os.path.getsize(paths[0])
        wasted = size * (len(paths) - 1)
        reclaimable += wasted
        print(f"[{i}] {len(paths)} copies · {human(size)} each · {human(wasted)} reclaimable")
        for p in paths:
            print(f"      {p}")
        print()
    print(f"Total reclaimable space: {human(reclaimable)}")


def main(argv=None):
    p = argparse.ArgumentParser(description="Find duplicate files by content.")
    p.add_argument("folder", help="Folder to scan recursively.")
    args = p.parse_args(argv)

    root = os.path.abspath(os.path.expanduser(args.folder))
    if not os.path.isdir(root):
        print(f"Error: {root} is not a directory.", file=sys.stderr)
        return 1

    print(f"Scanning {root} …\n")
    report(find_duplicates(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
