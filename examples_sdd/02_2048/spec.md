# Spec — 2048

A spec-driven example: this PRD is the contract. The **move/merge logic** — the
part with real rules and edge cases — lives in `iteration_1/logic.js` as pure
functions, and `iteration_1/test_logic.js` encodes the **Acceptance criteria**
below as Node tests. `index.html` is the thin presentation layer built on top.

**Overview**

A single-player 2048: a 4×4 grid of numbered tiles. Arrow keys slide every tile
in one direction; equal tiles that collide merge into one of double the value.
A new tile appears after each move that changes the board. Reach 2048 to win;
run out of moves to lose. Single self-contained page, vanilla JS + DOM, no build
step, no dependencies.

**Goals**

- Correct, classic 2048 rules — especially the merge semantics.
- A pure, deterministic logic core that is unit-tested independently of the UI.
- Playable and polished: keyboard + touch, score, best score, restart.

**Non-goals**

- No undo, no animations beyond simple tile transitions, no online leaderboard.
- No configurable board size or target — fixed 4×4, target 2048.

**User stories**

- As a player, I press an arrow key and every tile slides that way, merging equal
  neighbours, and a new tile appears if anything moved.
- As a player, I see my score climb by the value of each merge, and my best score
  persists between visits.
- As a player, I get a clear win at 2048 and a clear game-over when no moves
  remain, and I can start a new game instantly.

**Functional requirements**

1. The board is a 4×4 grid; empty cells are `0`. Tiles hold powers of two.
2. A move slides all tiles toward the chosen edge until they hit the wall or
   another tile.
3. Two tiles of equal value that collide merge into one tile of double value; the
   score increases by the merged value.
4. A tile may merge at most **once per move** — no chained double-merges
   (e.g. `[4,2,2]` sliding left → `[4,4]`, not `[8]`).
5. After any move that changes the board, spawn one new tile (a 2 with 90%
   probability, a 4 with 10%) in a random empty cell.
6. Winning: the game is won when any tile reaches 2048.
7. Losing: the game is over when the board is full and no adjacent equal tiles
   exist (no legal move in any direction).
8. Controls: arrow keys / WASD on desktop, swipe on touch devices.
9. Persist the best score in `localStorage`; a restart clears the board and score
   but keeps the best.

**Visual style**

Warm, classic 2048 look — rounded tiles on a padded board, tile colour keyed to
value, score and best in pill boxes, a win/lose overlay with a "New game" action.
Responsive down to mobile widths.

**Technical constraints**

- `logic.js` holds only pure functions (no DOM, no globals mutated): grids in,
  new grids out, with an injectable RNG for `spawnTile` so tests are
  deterministic. It exports for **both** the browser (`window.Game2048`) and Node
  (`module.exports`) so `index.html` and `test_logic.js` share one source.
- `index.html` loads `logic.js` via `<script src="logic.js">` (plain script, so it
  works when opened from `file://`) and handles render + input + storage.
- Standard library / platform only; runnable by opening the file, tests by
  `node test_logic.js`.

**Acceptance criteria**

Each bullet maps to a test in `iteration_1/test_logic.js`:

- Sliding compacts and merges a row once: `[2,0,2,0]→[4,0,0,0]` (+4),
  `[2,2,2,2]→[4,4,0,0]` (+8) (`test_slide_row`).
- No chained merges in a single move: `[4,2,2]→[4,4]`, `[2,2,2]→[4,2]`
  (`test_no_chained_merge`).
- Directional moves work via the same core: a right move mirrors, up/down
  transpose (`test_move_directions`).
- A move that changes nothing reports `moved === false`; a changing move reports
  `true` (`test_moved_flag`).
- `emptyCells` lists every empty coordinate; `spawnTile` with a stub RNG fills
  exactly one of them with a 2 or 4 (`test_spawn_tile`).
- `isWin` is true exactly when a 2048 tile is present (`test_is_win`).
- `hasMoves` is false only when the board is full with no adjacent equal tiles
  (`test_has_moves`).
- Score gained equals the sum of merged tile values for a move
  (`test_score_gained`).
