# Spec-Driven Examples

Two workshop examples built the **spec-driven development (SDD)** way:

1. Write the **spec first** — a PRD (`spec.md`) with explicit *Acceptance criteria*.
2. Encode those acceptance criteria as **automated tests**.
3. Build the implementation until the tests pass.

The point of these examples is the visible link between the spec and the tests:
every bullet under *Acceptance criteria* in a `spec.md` maps to a named test.

| # | Example | Type | Spec | Tests |
| --- | --- | --- | --- | --- |
| 01 | Markdown Table Formatter | Python CLI (stdlib) | [`01_markdown_table_formatter/spec.md`](01_markdown_table_formatter/spec.md) | `python3 test_mdtable.py` |
| 02 | 2048 | HTML/JS game (Canvas-free DOM) | [`02_2048/spec.md`](02_2048/spec.md) | `node test_logic.js` |

## Layout

```
examples_sdd/
  01_markdown_table_formatter/
    spec.md                       # PRD + acceptance criteria (the contract)
    iteration_1/
      mdtable.py                  # implementation
      test_mdtable.py             # one test per acceptance criterion
      messy_example.md            # demo fixture
  02_2048/
    spec.md
    iteration_1/
      logic.js                    # pure game logic (browser + Node)
      index.html                  # UI built on top of logic.js
      test_logic.js               # one test per acceptance criterion
```

## Running

**01 — Markdown Table Formatter**

```bash
cd 01_markdown_table_formatter/iteration_1
python3 test_mdtable.py                 # acceptance tests
python3 mdtable.py messy_example.md     # format a file
cat messy_example.md | python3 mdtable.py --align l,c,r
```

**02 — 2048**

```bash
cd 02_2048/iteration_1
node test_logic.js                      # acceptance tests for the game logic
# then open index.html in a browser to play
```

The 2048 game keeps its rules-heavy logic in `logic.js` as pure functions so the
same source runs in the browser **and** under Node for testing — the UI in
`index.html` is a thin layer on top.
