// logic.js — pure 2048 game logic, shared by index.html and test_logic.js.
//
// No DOM, no shared mutable state: functions take a grid (array of 4 rows of 4
// integers, 0 = empty) and return new values. Built spec-first — see ../spec.md.
// Exports for both the browser (window.Game2048) and Node (module.exports).

(function (root) {
  'use strict';

  var SIZE = 4;
  var TARGET = 2048;

  function emptyGrid() {
    var g = [];
    for (var r = 0; r < SIZE; r++) g.push([0, 0, 0, 0]);
    return g;
  }

  function clone(grid) {
    return grid.map(function (row) { return row.slice(); });
  }

  function equal(a, b) {
    for (var r = 0; r < SIZE; r++)
      for (var c = 0; c < SIZE; c++)
        if (a[r][c] !== b[r][c]) return false;
    return true;
  }

  // Slide + merge a single row to the LEFT. Returns { row, gained }.
  // A tile merges at most once per call (no chained double-merges).
  function slideRowLeft(row) {
    var nums = row.filter(function (v) { return v !== 0; });
    var out = [];
    var gained = 0;
    for (var i = 0; i < nums.length; i++) {
      if (i + 1 < nums.length && nums[i] === nums[i + 1]) {
        var merged = nums[i] * 2;
        out.push(merged);
        gained += merged;
        i++; // consume the partner so it can't merge again
      } else {
        out.push(nums[i]);
      }
    }
    while (out.length < row.length) out.push(0);
    return { row: out, gained: gained };
  }

  function transpose(grid) {
    var g = emptyGrid();
    for (var r = 0; r < SIZE; r++)
      for (var c = 0; c < SIZE; c++)
        g[c][r] = grid[r][c];
    return g;
  }

  function reverseRows(grid) {
    return grid.map(function (row) { return row.slice().reverse(); });
  }

  // Apply a move in direction 'left' | 'right' | 'up' | 'down'.
  // Returns { grid, gained, moved }.
  function move(grid, dir) {
    var work = clone(grid);
    if (dir === 'right') work = reverseRows(work);
    else if (dir === 'up') work = transpose(work);
    else if (dir === 'down') work = reverseRows(transpose(work));

    var gained = 0;
    work = work.map(function (row) {
      var res = slideRowLeft(row);
      gained += res.gained;
      return res.row;
    });

    if (dir === 'right') work = reverseRows(work);
    else if (dir === 'up') work = transpose(work);
    else if (dir === 'down') work = transpose(reverseRows(work));

    return { grid: work, gained: gained, moved: !equal(grid, work) };
  }

  function emptyCells(grid) {
    var cells = [];
    for (var r = 0; r < SIZE; r++)
      for (var c = 0; c < SIZE; c++)
        if (grid[r][c] === 0) cells.push([r, c]);
    return cells;
  }

  // Place a new tile (2 at 90%, 4 at 10%) in a random empty cell.
  // rng() must return a float in [0, 1); injectable for deterministic tests.
  function spawnTile(grid, rng) {
    rng = rng || Math.random;
    var cells = emptyCells(grid);
    if (!cells.length) return grid;
    var pick = cells[Math.floor(rng() * cells.length)];
    var value = rng() < 0.9 ? 2 : 4;
    var g = clone(grid);
    g[pick[0]][pick[1]] = value;
    return g;
  }

  function hasMoves(grid) {
    if (emptyCells(grid).length) return true;
    for (var r = 0; r < SIZE; r++) {
      for (var c = 0; c < SIZE; c++) {
        var v = grid[r][c];
        if (c + 1 < SIZE && grid[r][c + 1] === v) return true;
        if (r + 1 < SIZE && grid[r + 1][c] === v) return true;
      }
    }
    return false;
  }

  function isWin(grid, target) {
    target = target || TARGET;
    for (var r = 0; r < SIZE; r++)
      for (var c = 0; c < SIZE; c++)
        if (grid[r][c] >= target) return true;
    return false;
  }

  var API = {
    SIZE: SIZE,
    TARGET: TARGET,
    emptyGrid: emptyGrid,
    clone: clone,
    equal: equal,
    slideRowLeft: slideRowLeft,
    move: move,
    emptyCells: emptyCells,
    spawnTile: spawnTile,
    hasMoves: hasMoves,
    isWin: isWin,
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  if (typeof window !== 'undefined') window.Game2048 = API;
})(this);
