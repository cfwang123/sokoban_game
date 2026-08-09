/**
 * 推箱子核心逻辑（Node.js 教学）。
 * CommonJS 模块，与 goapp1 / rustapp1 对齐。
 */

'use strict';

function key(x, y) {
  return x + ',' + y;
}

function fromRows(rows, index) {
  var walls = Object.create(null);
  var goals = Object.create(null);
  var boxes = Object.create(null);
  var player = { x: 0, y: 0 };
  var maxX = 0;
  var maxY = 0;
  for (var y = 0; y < rows.length; y++) {
    maxY = y;
    var row = rows[y];
    for (var x = 0; x < row.length; x++) {
      if (x > maxX) maxX = x;
      var ch = row[x];
      var k = key(x, y);
      switch (ch) {
        case '#':
          walls[k] = true;
          break;
        case '.':
          goals[k] = true;
          break;
        case '$':
          boxes[k] = true;
          break;
        case '*':
          boxes[k] = true;
          goals[k] = true;
          break;
        case '@':
          player = { x: x, y: y };
          break;
        case '+':
          player = { x: x, y: y };
          goals[k] = true;
          break;
      }
    }
  }
  return {
    walls: walls,
    goals: goals,
    boxes: boxes,
    player: player,
    moves: 0,
    won: false,
    width: maxX + 1,
    height: maxY + 1,
    levelIndex: index || 0,
    hist: [],
  };
}

function checkWin(state) {
  for (var b in state.boxes) {
    if (!state.goals[b]) {
      state.won = false;
      return;
    }
  }
  state.won = true;
}

function tryMove(state, dx, dy) {
  if (state.won) return false;
  var nx = state.player.x + dx;
  var ny = state.player.y + dy;
  var nk = key(nx, ny);
  if (state.walls[nk]) return false;
  if (state.boxes[nk]) {
    var bx = nx + dx;
    var by = ny + dy;
    var bk = key(bx, by);
    if (state.walls[bk] || state.boxes[bk]) return false;
    state.hist.push({
      player: { x: state.player.x, y: state.player.y },
      boxFrom: nk,
      boxTo: bk,
    });
    delete state.boxes[nk];
    state.boxes[bk] = true;
    state.player = { x: nx, y: ny };
    state.moves++;
    checkWin(state);
    return true;
  }
  state.hist.push({
    player: { x: state.player.x, y: state.player.y },
    boxFrom: null,
    boxTo: null,
  });
  state.player = { x: nx, y: ny };
  return true;
}

function undo(state) {
  if (state.won || state.hist.length === 0) return false;
  var entry = null;
  while (state.hist.length > 0) {
    entry = state.hist.pop();
    if (entry.boxFrom) break;
    state.player = entry.player;
  }
  if (!entry || !entry.boxFrom) return true;
  state.player = entry.player;
  delete state.boxes[entry.boxTo];
  state.boxes[entry.boxFrom] = true;
  if (state.moves > 0) state.moves--;
  state.won = false;
  return true;
}

function renderAscii(state) {
  var lines = [];
  for (var y = 0; y < state.height; y++) {
    var row = '';
    for (var x = 0; x < state.width; x++) {
      var k = key(x, y);
      if (state.player.x === x && state.player.y === y) {
        row += state.goals[k] ? '+' : '@';
      } else if (state.boxes[k]) {
        row += state.goals[k] ? '*' : '$';
      } else if (state.walls[k]) {
        row += '#';
      } else if (state.goals[k]) {
        row += '.';
      } else {
        row += ' ';
      }
    }
    lines.push(row);
  }
  return lines.join('\n') + '\n';
}

/**
 * BFS 寻路：返回 [{dx,dy}, ...] 或 null。
 */
function findPath(state, tx, ty) {
  var sx = state.player.x;
  var sy = state.player.y;
  if (sx === tx && sy === ty) return [];
  var blocked = Object.create(null);
  var k;
  for (k in state.walls) blocked[k] = true;
  for (k in state.boxes) blocked[k] = true;
  var start = key(sx, sy);
  var target = key(tx, ty);
  var queue = [{ x: sx, y: sy }];
  var visited = Object.create(null);
  visited[start] = true;
  var parent = Object.create(null);
  var dirs = [
    { dx: 0, dy: -1 },
    { dx: 0, dy: 1 },
    { dx: -1, dy: 0 },
    { dx: 1, dy: 0 },
  ];
  while (queue.length > 0) {
    var cur = queue.shift();
    var ck = key(cur.x, cur.y);
    for (var i = 0; i < dirs.length; i++) {
      var d = dirs[i];
      var nx = cur.x + d.dx;
      var ny = cur.y + d.dy;
      var nk = key(nx, ny);
      if (blocked[nk] || visited[nk]) continue;
      visited[nk] = true;
      parent[nk] = { from: ck, dx: d.dx, dy: d.dy };
      if (nk === target) {
        var path = [];
        var p = nk;
        while (p !== start) {
          var info = parent[p];
          path.push({ dx: info.dx, dy: info.dy });
          p = info.from;
        }
        path.reverse();
        return path;
      }
      queue.push({ x: nx, y: ny });
    }
  }
  return null;
}

module.exports = {
  fromRows: fromRows,
  tryMove: tryMove,
  undo: undo,
  renderAscii: renderAscii,
  findPath: findPath,
};
