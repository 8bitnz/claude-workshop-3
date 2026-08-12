#!/usr/bin/env python3
"""mdtable.py — clean up and align a Markdown table.

Reads a messy, loosely-aligned pipe-delimited table (from a file argument or
stdin) and prints a tidy, column-aligned GitHub-flavored Markdown table.

Built spec-first: see ../spec.md. The pure functions below (parse_table,
column_widths, format_table, pad_cell) are what test_mdtable.py exercises; the
CLI is a thin wrapper around them. Standard library only.

Usage:
    python3 mdtable.py messy_example.md
    cat messy_example.md | python3 mdtable.py
    python3 mdtable.py messy_example.md --align l,c,r
"""
import argparse
import re
import sys

MIN_WIDTH = 3                       # so the separator "---" is always valid
ALIGN_CELL = re.compile(r"^:?-+:?$")  # matches an alignment-row cell like :--:
_ALIGN_WORD = {"l": "left", "c": "center", "r": "right",
               "left": "left", "center": "center", "right": "right"}


def split_row(line):
    """Split one table line into trimmed cells.

    Tolerates optional leading/trailing pipes and does not split on escaped
    pipes (``\\|``) inside a cell.
    """
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    parts = re.split(r"(?<!\\)\|", line)
    return [cell.strip() for cell in parts]


def is_alignment_row(cells):
    return bool(cells) and all(ALIGN_CELL.match(c) for c in cells)


def alignment_of(cell):
    left = cell.startswith(":")
    right = cell.endswith(":")
    if left and right:
        return "center"
    if right:
        return "right"
    return "left"


def parse_table(text):
    """Parse table text into (header, rows, aligns).

    Blank lines are ignored. The first non-blank row is the header. If the next
    row is an alignment row it is consumed to set per-column alignment; otherwise
    every column defaults to left.
    """
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("no table found in input")

    grid = [split_row(ln) for ln in lines]
    header = grid[0]
    ncols = len(header)
    aligns = ["left"] * ncols
    body = grid[1:]

    if body and is_alignment_row(body[0]):
        align_cells = body.pop(0)
        for i in range(ncols):
            if i < len(align_cells):
                aligns[i] = alignment_of(align_cells[i])

    # Normalise every row to the header's column count (pad short, keep header
    # width as the source of truth).
    rows = []
    for r in body:
        if len(r) < ncols:
            r = r + [""] * (ncols - len(r))
        elif len(r) > ncols:
            r = r[:ncols]
        rows.append(r)

    return header, rows, aligns


def escape_pipes(cell):
    # Escape only pipes that aren't already escaped.
    return re.sub(r"(?<!\\)\|", r"\\|", cell)


def column_widths(header, rows):
    ncols = len(header)
    widths = [MIN_WIDTH] * ncols
    for row in [header, *rows]:
        for i in range(ncols):
            widths[i] = max(widths[i], len(escape_pipes(row[i])))
    return widths


def pad_cell(text, width, align):
    text = escape_pipes(text)
    pad = max(0, width - len(text))
    if align == "right":
        return " " * pad + text
    if align == "center":
        left = pad // 2
        return " " * left + text + " " * (pad - left)
    return text + " " * pad          # left


def separator_cell(width, align):
    if align == "center":
        return ":" + "-" * (width - 2) + ":"
    if align == "right":
        return "-" * (width - 1) + ":"
    return "-" * width               # left (plain dashes)


def format_table(header, rows, aligns):
    widths = column_widths(header, rows)

    def render(cells):
        return "| " + " | ".join(
            pad_cell(cells[i], widths[i], aligns[i]) for i in range(len(header))
        ) + " |"

    lines = [render(header)]
    lines.append("| " + " | ".join(
        separator_cell(widths[i], aligns[i]) for i in range(len(header))) + " |")
    lines.extend(render(r) for r in rows)
    return "\n".join(lines)


def format_markdown(text, align_override=None):
    header, rows, aligns = parse_table(text)
    if align_override:
        words = [_ALIGN_WORD[a.strip().lower()] for a in align_override.split(",")]
        for i in range(len(aligns)):
            if i < len(words):
                aligns[i] = words[i]
    return format_table(header, rows, aligns)


def main(argv=None):
    p = argparse.ArgumentParser(description="Clean up and align a Markdown table.")
    p.add_argument("file", nargs="?", help="Table file (reads stdin if omitted).")
    p.add_argument("--align", help="Per-column alignment, e.g. 'l,c,r'.")
    args = p.parse_args(argv)

    text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    try:
        print(format_markdown(text, args.align))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
