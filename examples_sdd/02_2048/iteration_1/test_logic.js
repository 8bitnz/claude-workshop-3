// Acceptance tests for 2048 logic — one test per acceptance criterion in ../spec.md.
// Stdlib/platform only, no test runner: run `node test_logic.js`.

const G = require('./logic.js');

function assert(cond, msg) {
  if (!cond) throw new Error(msg || 'assertion failed');
}
function eq(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}
function assertEq(actual, expected, msg) {
  assert(eq(actual, expected),
    (msg || 'not equal') + '\n  expected ' + JSON.stringify(expected) +
    '\n  actual   ' + JSON.stringify(actual));
}

const tests = {};

tests.test_slide_row = function () {
  assertEq(G.slideRowLeft([2, 0, 2, 0]), { row: [4, 0, 0, 0], gained: 4 });
  assertEq(G.slideRowLeft([2, 2, 2, 2]), { row: [4, 4, 0, 0], gained: 8 });
  assertEq(G.slideRowLeft([0, 0, 0, 2]), { row: [2, 0, 0, 0], gained: 0 }); // just compaction
  assertEq(G.slideRowLeft([0, 0, 0, 0]), { row: [0, 0, 0, 0], gained: 0 });
};

tests.test_no_chained_merge = function () {
  // The freshly-merged 4 must not merge again with the leading 4.
  assertEq(G.slideRowLeft([4, 2, 2, 0]).row, [4, 4, 0, 0]);
  assertEq(G.slideRowLeft([2, 2, 2, 0]).row, [4, 2, 0, 0]);
  assertEq(G.slideRowLeft([2, 2, 2, 2]).row, [4, 4, 0, 0]);
};

tests.test_move_directions = function () {
  const grid = [
    [2, 0, 2, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [4, 0, 0, 4],
  ];
  assertEq(G.move(grid, 'left').grid[0], [4, 0, 0, 0]);
  assertEq(G.move(grid, 'right').grid[0], [0, 0, 0, 4]);
  assertEq(G.move(grid, 'right').grid[3], [0, 0, 0, 8]);
  // up: the two 2s in column 0/2 top rows and 4s stack upward
  const up = G.move([
    [2, 0, 0, 0],
    [2, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ], 'up').grid;
  assertEq(up[0], [4, 0, 0, 0]);
  // down: same column collapses to the bottom
  const down = G.move([
    [2, 0, 0, 0],
    [2, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ], 'down').grid;
  assertEq(down[3], [4, 0, 0, 0]);
};

tests.test_moved_flag = function () {
  const still = [
    [2, 4, 2, 4],
    [4, 2, 4, 2],
    [2, 4, 2, 4],
    [4, 2, 4, 2],
  ];
  assert(G.move(still, 'left').moved === false, 'no-op move should report moved=false');
  assert(G.move([[0, 0, 0, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 'left').moved === true,
    'a changing move should report moved=true');
};

tests.test_spawn_tile = function () {
  const grid = G.emptyGrid();
  grid[0][0] = 2; // one occupied cell -> 15 empties
  assert(G.emptyCells(grid).length === 15, 'emptyCells count');
  // Stub rng: first call picks the cell index (0 -> first empty), second sets value.
  let calls = 0;
  const rng = function () { calls++; return calls === 1 ? 0 : 0.5; }; // 0.5 < 0.9 -> a 2
  const g = G.spawnTile(grid, rng);
  const before = G.emptyCells(grid).length;
  const after = G.emptyCells(g).length;
  assert(after === before - 1, 'spawn fills exactly one empty cell');
  // find the newly placed tile
  let placed = null;
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++)
    if (g[r][c] !== 0 && !(r === 0 && c === 0)) placed = g[r][c];
  assert(placed === 2 || placed === 4, 'spawned tile is 2 or 4');
  assert(placed === 2, 'rng<0.9 spawns a 2');
};

tests.test_is_win = function () {
  assert(G.isWin([[2, 4, 8, 16], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2048]]) === true);
  assert(G.isWin([[2, 4, 8, 16], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1024]]) === false);
};

tests.test_has_moves = function () {
  const full_no_moves = [
    [2, 4, 2, 4],
    [4, 2, 4, 2],
    [2, 4, 2, 4],
    [4, 2, 4, 2],
  ];
  assert(G.hasMoves(full_no_moves) === false, 'gridlock has no moves');
  const full_with_pair = [
    [2, 2, 2, 4], // adjacent equal in top row
    [4, 2, 4, 2],
    [2, 4, 2, 4],
    [4, 2, 4, 2],
  ];
  assert(G.hasMoves(full_with_pair) === true, 'adjacent equal tiles => a move exists');
  const has_empty = G.emptyGrid();
  assert(G.hasMoves(has_empty) === true, 'empty cells => moves exist');
};

tests.test_score_gained = function () {
  // Two rows each merging a pair of 2s (=4) plus a pair of 4s (=8) => 12 per row.
  const grid = [
    [2, 2, 4, 4],
    [2, 2, 4, 4],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ];
  assert(G.move(grid, 'left').gained === 24, 'score equals sum of merged tiles');
};

let failures = 0;
Object.keys(tests).sort().forEach(function (name) {
  try {
    tests[name]();
    console.log('ok  ' + name);
  } catch (e) {
    failures++;
    console.log('FAIL ' + name + ' -> ' + e.message);
  }
});
if (failures) {
  console.log('\n' + failures + ' test(s) failed.');
  process.exit(1);
}
console.log('All tests passed.');
