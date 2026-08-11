# Example Games

Small, self-contained browser games built during the Claude Code workshop.
Each game is a single `index.html` (vanilla JS + Canvas, no build step, no
dependencies) living under `NN_name/iteration_1/`, matching the folder
convention used in `example_apps/` and `hero_apps/`.

| # | Game | Clone of | Controls |
| --- | --- | --- | --- |
| 01 | Asteroids | the arcade classic Asteroids | ← → rotate · ↑ thrust · Space fire |
| 02 | Boulder Dash | the dig-and-collect classic Boulder Dash | Arrow keys to move; push boulders sideways |
| 03 | Dino Run | Chrome's offline "no internet" dino game | Space / ↑ jump · ↓ duck · tap to jump |

## Running

Open any game's `index.html` directly in a browser:

```bash
open examples_games/01_asteroids/iteration_1/index.html
```

High scores are saved to `localStorage`, so they persist between visits.

## Notes

- **Asteroids** — vector ship with thrust/inertia and screen wrap; asteroids
  split into smaller ones when shot, and new waves grow as your score climbs.
- **Boulder Dash** — tile grid with falling-boulder physics (boulders and gems
  fall and roll off rounded surfaces). Collect enough diamonds to open the
  flashing exit; a boulder falling onto your head is fatal.
- **Dino Run** — endless runner that speeds up over time, with cacti to jump and
  birds to duck under, plus a persistent high score.
