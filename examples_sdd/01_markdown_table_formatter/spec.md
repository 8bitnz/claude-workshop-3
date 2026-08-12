# Spec — Markdown Table Formatter (`mdtable`)

A spec-driven example: this PRD is written **first**, its **Acceptance criteria**
are the contract, and `iteration_1/test_mdtable.py` encodes those criteria as
executable tests. The implementation (`mdtable.py`) exists to satisfy them.

**Overview**

A command-line tool that takes a messy, loosely-aligned pipe-delimited table and
prints a clean, column-aligned GitHub-flavored Markdown table. Input comes from a
file argument or standard input; output goes to standard output. Pure Python
standard library, no dependencies, no build step.

**Goals**

- Turn ragged, hand-typed Markdown tables into neatly aligned ones.
- Preserve and honour per-column alignment (left / center / right).
- Be a small, fully-deterministic, well-tested reference for spec-driven work.

**Non-goals**

- No rendering to HTML or other formats — Markdown in, Markdown out.
- No CSV/TSV parsing (that is a different tool); input is pipe-delimited.
- No cell content transformation (no wrapping, no Markdown-inside-cell layout).

**User stories**

- As a writer, I paste a lopsided Markdown table and get back a tidy, aligned one
  I can drop straight into a README.
- As a writer, I mark a column as right- or center-aligned and the output keeps
  that alignment, both in the separator row and in the padding.
- As a scripter, I pipe a table into the tool and get the formatted table on
  stdout so I can chain it in a shell pipeline.

**Functional requirements**

1. Read the table from a file path argument, or from stdin when no path is given.
2. Parse rows by splitting on the pipe character `|`, tolerating optional leading
   and trailing pipes, and trimming surrounding whitespace from every cell.
3. Treat the first row as the header and, if the second row is an alignment row
   (cells matching `:?-{1,}:?` with at least one dash), consume it to set
   per-column alignment; otherwise default every column to left alignment.
4. Support an explicit `--align` flag (e.g. `--align l,c,r`) that overrides any
   alignment row; values `l`/`c`/`r` map to left/center/right.
5. Pad ragged rows: rows with fewer cells than the header are padded with empty
   cells; the column count is taken from the header row.
6. Compute each column's width as the widest cell in that column, with a minimum
   of 3 so the separator (`---`) is always valid.
7. Render three parts — header, an alignment separator row using `:` markers that
   reflect each column's alignment, and the body — with every cell padded to its
   column width according to that column's alignment.
8. Escape any literal pipe characters inside cell content as `\|` so they don't
   break the table.
9. Print the formatted table to stdout with a trailing newline; exit non-zero
   with a clear message on unusable input (e.g. an empty table).

**Output format**

- Left column example `| name |`, right `| 12 |` padded on the left, center
  padded on both sides (extra space on the right when odd).
- Separator markers: left `:---` (or `---`), center `:--:`, right `---:`.
- Example: the input

  ```
  | Name | Qty | Price |
  |:-|-:|:-:|
  | Apple | 5 | 1.20 |
  | Fig | 12 | 3 |
  ```

  produces aligned columns with `Qty` right-aligned and `Price` centered.

**Technical constraints**

- Single file `mdtable.py`, Python 3, standard library only (`argparse` + string
  handling). No `pip install`.
- Pure formatting logic (`parse_table`, `column_widths`, `format_table`, and an
  alignment helper) is separated from CLI/IO so it is directly unit-testable.
- Runs as `python3 mdtable.py <file>` or `... | python3 mdtable.py`.

**Acceptance criteria**

Each bullet maps to a test in `iteration_1/test_mdtable.py`:

- Parsing strips whitespace and tolerates optional leading/trailing pipes
  (`test_parse_trims_and_tolerates_edge_pipes`).
- A `:--`/`:-:`/`--:` alignment row is detected and removed from the data, and
  sets per-column alignment (`test_alignment_row_detected`).
- `--align l,c,r` overrides the alignment row (`test_align_flag_overrides`).
- Column width equals the widest cell, with a floor of 3
  (`test_widths_use_widest_cell_min_three`).
- Left/center/right padding is correct, including the odd-width center case
  (`test_padding_per_alignment`).
- The separator row renders the correct `:` markers per alignment
  (`test_separator_markers`).
- Ragged rows are padded to the header's column count
  (`test_ragged_rows_padded`).
- Literal pipes inside cells are escaped as `\|` (`test_escapes_pipes`).
- Empty input raises a `ValueError` (`test_empty_input_rejected`).
- End-to-end: formatting an already-clean table is idempotent
  (`test_format_is_idempotent`).
