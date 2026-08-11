# Claude Code Workshop: 3 Simple Browser Games

Three recognisable arcade games, each scoped so Claude Code can build a working,
playable version from **one prompt**. No API keys, no paid dependencies, no build
step — each game is a single self-contained `index.html` (vanilla JS + Canvas).
Build each in its own `NN_name/iteration_1/` folder, matching the convention in
`example_apps/` and `hero_apps/`.

---

## 1. Asteroids
**Clone of:** the arcade classic *Asteroids*.
**Format:** single-file HTML/JS (Canvas)

**Prompt 1 — Build:**
> Build a single-file HTML/JS game called "Asteroids", a clone of the arcade
> classic, using Canvas and vanilla JS (no libraries, no build step). A triangular
> ship sits in the centre of a dark playfield. Rotate it with the left/right arrow
> keys, thrust with the up arrow (momentum and inertia, with screen-wrap at the
> edges), and fire bullets with Space. Large asteroids drift and wrap around the
> screen; shooting one splits it into two smaller asteroids, and the smallest ones
> are destroyed outright, each worth points. The ship has 3 lives, gets a brief
> invulnerability blink after respawning, and the game ends when lives run out.
> Show score and lives, persist a high score in localStorage, and have a start
> screen and a game-over screen with a restart. Neon vector styling, smooth 60fps.

---

## 2. Boulder Dash
**Clone of:** the dig-and-collect classic *Boulder Dash*.
**Format:** single-file HTML/JS (Canvas, tile grid)

**Prompt 1 — Build:**
> Build a single-file HTML/JS game called "Boulder Dash", a clone of the classic
> tile-based digging game, using Canvas and vanilla JS (no libraries, no build
> step). The level is a grid of tiles: steel walls, diggable dirt, boulders,
> diamonds, an exit, and the player. Move the player with the arrow keys, tunnelling
> through dirt as you go. Boulders and diamonds obey gravity — they fall into empty
> space below and roll off the rounded tops of other boulders/walls into gaps. The
> player can push a boulder sideways if there's an empty space beyond it. Collect
> enough diamonds to open the exit (make it flash when open), then reach it to win.
> A boulder or diamond falling directly onto the player's head is fatal. Track
> diamonds collected vs. required, score, and lives, with a start screen and
> game-over / win screens. Retro pixel styling.

---

## 3. Dino Run
**Clone of:** Chrome's offline "no internet" dinosaur game.
**Format:** single-file HTML/JS (Canvas)

**Prompt 1 — Build:**
> Build a single-file HTML/JS game called "Dino Run", a clone of Chrome's offline
> dinosaur game, using Canvas and vanilla JS (no libraries, no build step). A little
> dino runs on the spot at the left of the screen while the world scrolls past.
> Press Space or the up arrow (or tap) to jump over cacti, and hold the down arrow
> to duck under flying birds. The scroll speed increases gradually the longer you
> survive, obstacles spawn at randomised gaps, and the score ticks up over time.
> Colliding with any obstacle ends the run; show a game-over screen with a restart,
> and persist the high score in localStorage. Minimal monochrome styling in the
> spirit of the original, and it should respect the browser's dark mode.

---

### Facilitator notes
- Each game is a single-prompt build — paste the prompt into Claude Code and time
  how long it takes to get something playable.
- All three avoid external assets and libraries, so they run offline and in any
  workshop network conditions.
- Good candidates for a follow-up iteration prompt (add mobile touch controls,
  levels, sound, a pause menu) if there's time.
