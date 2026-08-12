"""Acceptance tests for mdtable — one test per acceptance criterion in spec.md.

Stdlib only, no test runner needed: run `python3 test_mdtable.py`.
"""
from mdtable import (
    split_row,
    is_alignment_row,
    alignment_of,
    parse_table,
    escape_pipes,
    column_widths,
    pad_cell,
    separator_cell,
    format_table,
    format_markdown,
)


def test_parse_trims_and_tolerates_edge_pipes():
    assert split_row("| a | b |") == ["a", "b"]        # leading + trailing pipes
    assert split_row("a | b") == ["a", "b"]            # no edge pipes
    assert split_row("|  x  |y|") == ["x", "y"]        # inner whitespace trimmed


def test_alignment_row_detected():
    text = "| Name | Qty | Price |\n| :- | -: | :-: |\n| Apple | 5 | 1.20 |"
    header, rows, aligns = parse_table(text)
    assert header == ["Name", "Qty", "Price"]
    assert aligns == ["left", "right", "center"]        # from the :- / -: / :-: row
    assert rows == [["Apple", "5", "1.20"]]             # alignment row removed from data
    assert is_alignment_row([":-", "-:", ":-:"]) is True
    assert is_alignment_row(["a", "-:"]) is False
    assert alignment_of(":-:") == "center" and alignment_of("--:") == "right"


def test_align_flag_overrides():
    text = "| a | b | c |\n| :- | :- | :- |\n| 1 | 2 | 3 |"
    _, _, aligns = parse_table(text)
    assert aligns == ["left", "left", "left"]
    out = format_markdown(text, align_override="l,c,r")
    # centered 'b' and right 'c' show up in the separator row
    assert "| :-: |" in out.splitlines()[1] or ":-:" in out.splitlines()[1]
    assert out.splitlines()[1].endswith("--: |")       # last column right-aligned


def test_widths_use_widest_cell_min_three():
    header = ["Name", "Qty", "X"]
    rows = [["Apple", "5", "y"]]
    assert column_widths(header, rows) == [5, 3, 3]     # "Apple"=5; others floored to 3


def test_padding_per_alignment():
    assert pad_cell("5", 3, "right") == "  5"
    assert pad_cell("Name", 5, "left") == "Name "
    assert pad_cell("3", 5, "center") == "  3  "        # even padding
    assert pad_cell("x", 4, "center") == " x  "         # odd: extra space on the right


def test_separator_markers():
    assert separator_cell(5, "left") == "-----"
    assert separator_cell(3, "right") == "--:"
    assert separator_cell(5, "center") == ":---:"


def test_ragged_rows_padded():
    text = "| a | b | c |\n| 1 |\n| 1 | 2 | 3 | 4 |"
    _, rows, _ = parse_table(text)
    assert rows[0] == ["1", "", ""]                     # short row padded
    assert rows[1] == ["1", "2", "3"]                   # extra cell dropped to header width


def test_escapes_pipes():
    assert escape_pipes("a|b") == "a\\|b"               # raw pipe escaped
    assert escape_pipes("a\\|b") == "a\\|b"             # already-escaped left alone
    # a cell that arrives already escaped survives a round trip
    header, rows, _ = parse_table("| x | y |\n| a \\| b | c |")
    assert rows == [["a \\| b", "c"]]


def test_empty_input_rejected():
    for bad in ["", "   ", "\n\n"]:
        try:
            parse_table(bad)
        except ValueError:
            continue
        raise AssertionError("expected ValueError for empty input")


def test_full_example():
    text = (
        "| Name | Qty | Price |\n"
        "| :- | -: | :-: |\n"
        "| Apple | 5 | 1.20 |\n"
        "| Fig | 12 | 3 |"
    )
    expected = (
        "| Name  | Qty | Price |\n"
        "| ----- | --: | :---: |\n"
        "| Apple |   5 | 1.20  |\n"
        "| Fig   |  12 |   3   |"
    )
    assert format_markdown(text) == expected


def test_format_is_idempotent():
    text = "| a | b |\n| - | - |\n| 1 | 2 |"
    once = format_markdown(text)
    twice = format_markdown(once)
    assert once == twice                                # formatting a clean table is stable


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("All tests passed.")
