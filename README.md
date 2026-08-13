# Claude Code Workshop — Demo Apps

A collection of small, self-contained applications built during a Claude Code
workshop. Each app was generated from a written prompt and then extended across
several iterations, so the repo doubles as a set of worked examples for
**scoping, building, and iterating on software with Claude Code**.

Every app is dependency-free: the HTML/JS apps are single files you open in a
browser (no build step), and the Python apps use only the standard library
(no `pip install`).

## Repository layout

```
hero_apps/       # larger "hero" demos, each built + extended live
example_apps/    # 10 quick single-prompt apps, each with 2 follow-up iterations
examples_games/  # small browser games, each a single-prompt build
examples_sdd/    # spec-driven examples: PRD + tests, then the implementation
```

Each app lives in its own folder, and **each iteration is a complete copy of the
app** in an `iteration_N/` subfolder, so you can see exactly how it grew from one
prompt to the next. The original prompt specs are kept alongside the code:

- `hero_apps/hero_apps.md`
- `example_apps/app_prompts.md`
- `examples_games/game_prompts.md`
- `examples_sdd/*/spec.md` (a full PRD per example)

## Hero apps (`hero_apps/`)

| App | What it is | Iterations |
| --- | --- | --- |
| `hero_app_1/` | **Engagement Book** — a fractional-CTO enquiry/quote tool with pricing, capacity tracking, and branded PDF proposals (Python web app). See the folder's own notes below. | single build |
| `kudos_wall/` | Team shoutout board with categories, then emoji reactions, then a "Kudos of the Week" spotlight + leaderboard. | 1–3 |
| `kudos_wall_v2/` | A second, independent take on the same Kudos Wall prompt — same six features, different build. | 1 |
| `neon_snake/` | Polished neon-styled Snake game — canvas, keyboard + swipe controls, high score. | 1 |
| `trip_split/` | Group trip expense splitter with correct settle-up math, flexible splits/categories, dark mode, and copy-to-clipboard summary. | 1–3 |

## Example apps (`example_apps/`)

Each folder has three iterations: the initial build plus two follow-up prompts.

| # | App | Format | Grows from → to |
| --- | --- | --- | --- |
| 01 | Meeting Cost Calculator | HTML | live cost counter → meeting history → shareable summary |
| 02 | Standup Note Builder | HTML | preview/copy → weekly history → carry-forward |
| 03 | Local Kanban Board | HTML | drag-drop board → due dates/priority → done-today + archive |
| 04 | Habit Tracker Grid | HTML | streak grid → effort gradient + % → CSV export + summary |
| 05 | Focus Timer | Python (tkinter) | Pomodoro + CSV log → break cycle → stats window |
| 06 | Downloads Declutterer | Python (CLI) | sort by type (dry-run/apply) → `--older-than-days` → collisions + `--undo` |
| 07 | Duplicate File Finder | Python (CLI) | hash report → interactive delete → `--keep-newest --auto` + log |
| 08 | Timesheet → Invoice | Python (CLI) | HTML invoice → expenses section → tax + companion CSV |
| 09 | Decision Matrix | HTML | weighted table → bar chart → save/load named matrices |
| 10 | Automation Effort Calculator | HTML | budget sliders → $/people ROI → ranked list + scatter plot |

## Example games (`examples_games/`)

Small, self-contained browser games (single-file HTML + Canvas, no build step),
each under `NN_name/iteration_1/`.

| # | Game | Clone of | Controls |
| --- | --- | --- | --- |
| 01 | Asteroids | the arcade classic Asteroids | ← → rotate · ↑ thrust · Space fire |
| 02 | Boulder Dash | the dig-and-collect classic Boulder Dash | Arrow keys; push boulders sideways |
| 03 | Dino Run | Chrome's offline "no internet" dino game | Space / ↑ jump · ↓ duck · tap to jump |

## Spec-driven examples (`examples_sdd/`)

Two examples built **spec-first**: each has a PRD (`spec.md`) whose *Acceptance
criteria* are encoded as automated tests, and the implementation is written to
pass them. Every acceptance-criteria bullet maps to a named test.

| # | Example | Type | Spec → tests |
| --- | --- | --- | --- |
| 01 | Markdown Table Formatter | Python CLI (stdlib) | `spec.md` → `python3 test_mdtable.py` |
| 02 | 2048 | HTML/JS game | `spec.md` → `node test_logic.js` |

The 2048 example keeps its rules-heavy logic in `logic.js` as pure functions, so
the same source runs in the browser (via `index.html`) **and** under Node for
testing.

## Running the apps

**HTML/JS apps and games** — open the `index.html` in any iteration folder
directly in a browser. No server, no build step. State (and high scores) is
saved to `localStorage`.

```bash
# e.g. macOS
open example_apps/03_local_kanban_board/iteration_3/index.html
```

**Python CLI apps** (06, 07, 08) — run with Python 3, standard library only.

```bash
python3 example_apps/06_downloads_declutterer/iteration_3/declutter.py --help
```

**Python GUI app** (05 Focus Timer) — needs a desktop environment with tkinter.

```bash
python3 example_apps/05_focus_timer/iteration_3/focus_timer.py
```

**Spec-driven examples' tests** — stdlib Python and Node, no runner needed:

```bash
python3 examples_sdd/01_markdown_table_formatter/iteration_1/test_mdtable.py
node    examples_sdd/02_2048/iteration_1/test_logic.js
```

## About `hero_apps/hero_app_1` (Engagement Book)

This is the most fully-featured app in the repo — a one-person fractional-CTO
engagement book that logs enquiries, scopes them (day rate + pass-through
handling + GST), tracks won/pending/lost status and monthly capacity, and
generates branded one-page PDF proposals. It has its own tests
(`test_engagements.py`) and runs as a local web app:

```bash
cd hero_apps/hero_app_1
python3 app.py          # then open http://localhost:8000
python3 test_engagements.py
```

Its pricing, capacity thresholds, and data format are documented in comments and
constants within `engagements.py`.

## License

This project is licensed under the **[PolyForm Noncommercial License 1.0.0](LICENSE)**.

In short: you're free to use, modify, and share everything here for any
**non-commercial** purpose — personal projects, learning, teaching, research, and
use by non-profits or educational institutions. **Commercial use, including
selling the code or products built from it, is not permitted.** Keep the
copyright notice intact when you share it.

This is a *source-available* license, not an OSI-approved open-source license
(open-source licenses can't restrict commercial use). If you'd like to use any of
this commercially, get in touch with the author.
