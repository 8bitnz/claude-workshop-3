# Claude Code Workshop — Three Additional Hero Apps

Three demo apps, each teaching a different Claude Code skill: extending an existing codebase, autonomous spec-driven building, and iterative prompting.

---

## 1. Pre-built, extended live — "Kudos Wall"

**Teaches:** working inside an existing codebase — reading structure, respecting existing patterns, scoping a feature request.

**Concept:** A single-page team shoutout board. People post a kudos card (from, to, message, category tag like Teamwork / Creativity / Above & Beyond). Cards render in a grid, newest first, saved to localStorage. Build this in advance so the session opens on something already polished — then extend it live so the room sees Claude Code navigate real, pre-existing code rather than generating from a blank file.

Pick one live extension depending on time and audience energy, or run both back to back.

### Prompt 1 — Advance build (run before the workshop)

```
Build a single-page web app called Kudos Wall. It's a shoutout board where
teammates post public kudos to each other.

Features:
- A form to post a kudos: sender name, recipient name, message (short, ~140
  chars), and a category chosen from Teamwork, Creativity, Above & Beyond,
  Leadership.
- Posted kudos appear as cards in a responsive grid, newest first.
- Each card shows the category as a colored tag, the message, and "from X
  to Y".
- Persist kudos in localStorage so the wall survives a page refresh.
- A simple filter bar to show only kudos for a given recipient.
- Clean, warm, modern visual style — this needs to look good projected on a
  screen. Single HTML file, vanilla JS and CSS, no build step, no backend.

Ship something that works end to end, not a skeleton.
```

### Prompt 2 — Live feature add, option A (reactions)

```
Add emoji reactions to each kudos card. People should be able to click a
small set of reaction emoji (👏 🎉 ❤️ 🔥) under any card, see a live count
per emoji, and toggle their own reaction off by clicking again. Store
reactions in the same localStorage structure as the kudos data — don't
introduce a separate storage scheme. Keep the visual style consistent with
the rest of the app.
```

### Prompt 3 — Live feature add, option B (kudos of the week + leaderboard)

```
Add a "Kudos of the Week" spotlight at the top of the wall — the most
recently posted kudos in the last 7 days with the most reactions (or most
recent if there are no reactions yet), shown in a larger highlighted card.
Below it, add a small leaderboard showing the top 3 recipients by number of
kudos received all-time. Recompute both whenever kudos data changes. Match
the existing visual style.
```

**Facilitator note:** having two independent feature-add prompts ready means you can pick whichever fits the room's remaining time, or take a vote.

---

## 2. 15-minute autonomous build — "Neon Snake"

**Teaches:** writing a spec tight enough that Claude Code can build the whole thing unattended, and reviewing an agent's completed work against acceptance criteria.

**Concept:** A polished, playable browser version of Snake with a neon aesthetic — instantly recognizable, satisfying to watch take shape, and small enough in scope to realistically finish inside the slot. Start the build at the top of the session, let it run while you narrate what's happening, and play it live at the end.

### PRD — Neon Snake

**Overview**
A single-player Snake game playable in the browser, built as one self-contained HTML file (inline CSS and JS, no build step, no external dependencies, no backend). Retro-arcade / neon visual style.

**Goals**
- A complete, playable, bug-free game by the end of the build.
- Visually striking — this is a live demo piece, not a prototype.
- Playable via keyboard and on touch/mobile.

**Non-goals**
- No multiplayer, no accounts, no server-side leaderboard.
- No level editor or multiple game modes — one polished mode only.

**User stories**
- As a player, I press an arrow key (or swipe on mobile) to change the snake's direction and see it respond immediately.
- As a player, I eat food pellets to grow the snake and increase my score.
- As a player, I lose when the snake hits a wall or itself, and I see a clear game-over state with my score.
- As a player, I can see my personal high score, saved between visits.
- As a player, I can restart instantly without reloading the page.

**Functional requirements**
1. Canvas-based game board on a dark background with a visible grid.
2. Snake moves continuously in the last direction chosen; cannot reverse directly into itself.
3. Food spawns at a random empty cell after each pellet is eaten.
4. Score increments per pellet eaten; speed increases gradually as score rises.
5. Collision with walls or the snake's own body ends the game.
6. Game-over screen shows final score, high score, and a "Play Again" action.
7. High score persists via localStorage.
8. Keyboard controls (arrow keys / WASD) and on-screen touch controls or swipe support for mobile.
9. Start screen with brief instructions before the first game begins.

**Visual style**
Neon color palette (electric green/cyan snake, magenta or amber food, near-black background), subtle glow/shadow effects, smooth animation, a heading/title treated as a mini arcade marquee.

**Technical constraints**
- Single `.html` file, vanilla JS, inline CSS. No frameworks, no npm install, no build tooling.
- Must run by opening the file directly in a browser.
- Should perform smoothly at 60fps on a typical laptop.

**Acceptance criteria**
- Opening the file immediately shows a working start screen.
- A full game can be played start to finish with no console errors.
- Score and high score behave correctly across multiple games and a page refresh.
- Layout doesn't break on a resized/mobile-width window.

---

## 3. Three-iteration build — "Trip Split"

**Teaches:** scoping a first prompt deliberately small, then layering in complexity and polish across separate, focused prompts rather than trying to get everything in one shot.

**Concept:** A group expense splitter for trips — add people, log who paid for what, see who owes whom. Recognizable, has natural depth (splitting logic, multiple people, math that needs to be right), and gives a clean before/after story across three passes.

### Prompt 1 — Initial build (MVP)

```
Build a single-page web app called Trip Split for splitting group expenses
on a trip.

Core features:
- Add people to the trip by name.
- Log an expense: description, amount, who paid, and which people it should
  be split evenly among (default: everyone).
- Show a running list of all expenses.
- Show a summary of net balances per person (how much they're owed or owe
  overall) and a simple settle-up list of "who pays whom, how much" that
  minimizes the number of transactions.
- Store everything in localStorage so it survives a refresh.

Single HTML file, vanilla JS and CSS, no build step, no backend. It should
work correctly end to end — the math is the most important part, get it
right.
```

### Prompt 2 — Feature add

```
Extend Trip Split with more flexible expense splitting:
- Allow an expense to be split by exact custom amounts per person (must sum
  to the total) as an alternative to even split.
- Allow an expense to be split by percentage per person (must sum to 100%).
- Add expense categories (Food, Transport, Lodging, Activities, Other) with
  a small icon or tag per category.
- Allow editing and deleting existing expenses, recalculating balances
  afterward.
- Add a per-category spending breakdown to the summary view.

Keep all of this working with the existing balance and settle-up logic —
don't rewrite what already works.
```

### Prompt 3 — Fine-tuning / polish

```
Polish Trip Split for something I'd actually show people:
- Redesign the visual style to feel modern and trustworthy — clear
  typography, good spacing, a coherent color palette, and a dark mode
  toggle.
- Add empty states for a trip with no people or no expenses yet.
- Make it fully usable on mobile widths.
- Add a "Copy summary" action that puts a clean, readable text version of
  the balances and settle-up list on the clipboard, so it can be pasted
  into a group chat.
- Add small, tasteful transitions/animations when expenses are added or
  the summary updates — nothing gimmicky.
- Do a pass for edge cases: someone with no expenses, a trip with one
  person, deleting the last expense, very long names or descriptions.

Don't change the underlying split logic — this pass is about UI, UX, and
robustness.
```
