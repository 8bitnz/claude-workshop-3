#!/usr/bin/env python3
"""find_dupes.py — find duplicate files by content (standard library only).

Walks a folder recursively, groups files with identical content using an MD5
hash (read in chunks so large files are fine), and reports the duplicate groups
and how much space could be reclaimed.

Add --interactive to walk each duplicate group and choose which copies to
delete (with a confirmation before anything is removed).

Usage:
    python3 find_dupes.py /path/to/folder
    python3 find_dupes.py /path/to/folder --interactive
"""
import argparse
import hashlib
import os
import sys
from datetime import datetime

CHUNK = 65536  # 64 KB
LOG_NAME = "dupes_removed.log"


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


def interactive(groups):
    if not groups:
        print("No duplicate files found. 🎉")
        return
    freed = 0
    for i, (h, paths) in enumerate(groups.items(), 1):
        size = os.path.getsize(paths[0])
        print(f"\nGroup {i}/{len(groups)} · {human(size)} each")
        for n, p in enumerate(paths, 1):
            print(f"  [{n}] {p}")
        choice = input("Delete which? (e.g. '2 3', 's' to skip, 'q' to quit): ").strip().lower()
        if choice == "q":
            break
        if choice in ("", "s"):
            continue
        try:
            nums = sorted({int(x) for x in choice.split()})
        except ValueError:
            print("  Didn't understand that — skipping group.")
            continue
        targets = [paths[n - 1] for n in nums if 1 <= n <= len(paths)]
        if len(targets) == len(paths):
            print("  That would delete every copy — keeping at least one. Skipping.")
            continue
        if not targets:
            continue
        print("  About to delete:")
        for t in targets:
            print(f"    {t}")
        if input("  Confirm? (y/N): ").strip().lower() == "y":
            for t in targets:
                try:
                    tsize = os.path.getsize(t)
                    os.remove(t)
                    freed += tsize
                    print(f"    deleted {t}")
                except OSError as e:
                    print(f"    could not delete {t}: {e}")
        else:
            print("  Skipped.")
    print(f"\nDone. Freed {human(freed)}.")


def log_deletion(root, path, size):
    with open(os.path.join(root, LOG_NAME), "a") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')}\t{size}\t{path}\n")


def auto_keep_newest(root, groups):
    """Delete all but the most recently modified file in each group."""
    if not groups:
        print("No duplicate files found. 🎉")
        return
    freed = 0
    deleted = 0
    for h, paths in groups.items():
        newest = max(paths, key=lambda p: os.path.getmtime(p))
        for p in paths:
            if p == newest:
                continue
            try:
                size = os.path.getsize(p)
                os.remove(p)
                log_deletion(root, p, size)
                freed += size
                deleted += 1
                print(f"  deleted {p}")
                print(f"    kept   {newest}")
            except OSError as e:
                print(f"  could not delete {p}: {e}")
    print(f"\nDeleted {deleted} file(s), freed {human(freed)}. Logged to {LOG_NAME}.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Find duplicate files by content.")
    p.add_argument("folder", help="Folder to scan recursively.")
    p.add_argument("--interactive", action="store_true",
                   help="Choose which duplicates to delete, group by group.")
    p.add_argument("--keep-newest", action="store_true",
                   help="In each group, keep the most recently modified copy.")
    p.add_argument("--auto", action="store_true",
                   help="With --keep-newest, delete the others without prompting.")
    args = p.parse_args(argv)

    root = os.path.abspath(os.path.expanduser(args.folder))
    if not os.path.isdir(root):
        print(f"Error: {root} is not a directory.", file=sys.stderr)
        return 1

    print(f"Scanning {root} …\n")
    groups = find_duplicates(root)
    report(groups)

    if args.keep_newest and args.auto:
        print("\nAuto-deleting all but the newest copy in each group:\n")
        auto_keep_newest(root, groups)
    elif args.keep_newest:
        print("\n--keep-newest requires --auto to actually delete. Nothing removed.")
    elif args.interactive:
        interactive(groups)
    return 0


if __name__ == "__main__":
    sys.exit(main())
