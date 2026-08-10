# AGENTS.md

Guidance for AI coding agents (such as Claude Code) working in this
repository. Human contributors are welcome to read this too — it documents
the conventions we expect everyone to follow.

This file is intentionally short and practical. Keep it up to date as the
project grows.

---

## Project overview

**Claude Workshop 3 — Code** is a Python-based sandbox used to teach
agent-assisted development. There is no shipping product; the goal is to
practice clean, reviewable workflows. Optimize for clarity and teachability
over cleverness.

---

## Environment setup

- Target **Python 3.10+**.
- Use a virtual environment:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```
- Install dependencies from `requirements.txt` or `pyproject.toml` when they
  exist. If neither is present yet, the project has no third-party
  dependencies.

---

## Build, test, and lint commands

Use these commands when they apply. If a tool is not yet configured, note it
rather than assuming it is missing.

| Task | Command |
|------|---------|
| Run tests | `pytest` |
| Run a single test | `pytest path/to/test_file.py::test_name` |
| Lint | `ruff check .` |
| Format | `ruff format .` (or `black .`) |
| Type-check | `mypy .` |

Always run the tests before committing. If you add behavior, add a test for
it.

---

## Coding conventions

- Follow **PEP 8**. Prefer `ruff`/`black` defaults for formatting.
- Use clear, descriptive names; avoid abbreviations.
- Add **type hints** to public functions.
- Write **docstrings** for modules and non-trivial functions.
- Keep functions small and focused. Prefer pure functions where practical.
- Match the style of the surrounding code — comment density, naming, and
  idiom.

---

## Testing conventions

- Tests live in a `tests/` directory and are named `test_*.py`.
- Use `pytest`. Keep tests fast and deterministic.
- Cover the happy path **and** at least one edge case for new logic.
- A change is not done until the tests pass.

---

## Git and pull request workflow

- **Never commit directly to `main`.** Create a feature branch:
  ```bash
  git checkout -b your-name/short-description
  ```
- Make **focused commits** with clear, imperative messages
  (e.g. "Add greeting module", not "changes").
- Keep pull requests small and reviewable — a series of tidy commits beats
  one giant diff.
- Ensure tests and linters pass before pushing.
- **Do not open a pull request unless explicitly asked to.**

---

## What to do / what to avoid

**Do:**

- Ask clarifying questions when a task is ambiguous.
- Explain your plan before making large changes.
- Leave the working tree clean (no stray temp files).

**Avoid:**

- Committing secrets, credentials, or `.env` files.
- Large, unrelated refactors bundled into one change.
- Deleting or rewriting files you did not create without confirming first.
- Adding dependencies without a clear reason.

---

## Safety notes

- This is a teaching repo; prefer readable solutions over optimized ones.
- If a change is hard to reverse or affects shared state, confirm first.
- Report outcomes honestly — if tests fail, say so and show the output.
