/**
 * electronapp1 渲染进程：迷你关卡 + Canvas（仿 html_app）
 */
'use strict';

(function () {
  var CELL = 40;
  var PAD = 20;
  var LEVEL = [
    '#######',
    '#. . .#',
    '# $$$ #',
    '#.$@$.#',
    '# $$$ #',
    '#. . .#',
    '#######',
  ];

  var canvas = document.getElementById('c');
  var ctx = canvas.getContext('2d');
  var hud = document.getElementById('hud');
  var state = null;

  function key(x, y) { return x + ',' + y; }

  function fromRows(rows) {
    var walls = {}, goals = {}, boxes = {}, player = { x: 0, y: 0 };
    var maxX = 0, maxY = 0;
    for (var y = 0; y < rows.length; y++) {
      maxY = y;
      for (var x = 0; x < rows[y].length; x++) {
        if (x > maxX) maxX = x;
        var ch = rows[y][x];
        var k = key(x, y);
        if (ch === '#') walls[k] = true;
        else if (ch === '.') goals[k] = true;
        else if (ch === '$') boxes[k] = true;
        else if (ch === '*') { boxes[k] = true; goals[k] = true; }
        else if (ch === '@') player = { x: x, y: y };
        else if (ch === '+') { player = { x: x, y: y }; goals[k] = true; }
      }
    }
    return {
      walls: walls, goals: goals, boxes: boxes, player: player,
      moves: 0, won: false, width: maxX + 1, height: maxY + 1, hist: [],
    };
  }

  function checkWin() {
    for (var b in state.boxes) {
      if (!state.goals[b]) { state.won = false; return; }
    }
    state.won = true;
  }

  function tryMove(dx, dy) {
    if (!state || state.won) return;
    var nx = state.player.x + dx, ny = state.player.y + dy;
    var nk = key(nx, ny);
    if (state.walls[nk]) return;
    if (state.boxes[nk]) {
      var bx = nx + dx, by = ny + dy, bk = key(bx, by);
      if (state.walls[bk] || state.boxes[bk]) return;
      state.hist.push({ player: { x: state.player.x, y: state.player.y }, boxFrom: nk, boxTo: bk });
      delete state.boxes[nk];
      state.boxes[bk] = true;
      state.player = { x: nx, y: ny };
      state.moves++;
      checkWin();
      paint();
      return;
    }
    state.hist.push({ player: { x: state.player.x, y: state.player.y }, boxFrom: null, boxTo: null });
    state.player = { x: nx, y: ny };
    paint();
  }

  function undo() {
    if (!state || state.won || !state.hist.length) return;
    var e = null;
    while (state.hist.length) {
      e = state.hist.pop();
      if (e.boxFrom) break;
      state.player = e.player;
    }
    if (!e || !e.boxFrom) { paint(); return; }
    state.player = e.player;
    delete state.boxes[e.boxTo];
    state.boxes[e.boxFrom] = true;
    if (state.moves > 0) state.moves--;
    state.won = false;
    paint();
  }

  function findPath(tx, ty) {
    var sx = state.player.x, sy = state.player.y;
    if (sx === tx && sy === ty) return [];
    var blocked = {};
    var k;
    for (k in state.walls) blocked[k] = true;
    for (k in state.boxes) blocked[k] = true;
    var start = key(sx, sy), target = key(tx, ty);
    var q = [{ x: sx, y: sy }];
    var visited = {}; visited[start] = true;
    var parent = {};
    var dirs = [{ dx: 0, dy: -1 }, { dx: 0, dy: 1 }, { dx: -1, dy: 0 }, { dx: 1, dy: 0 }];
    while (q.length) {
      var cur = q.shift();
      var ck = key(cur.x, cur.y);
      for (var i = 0; i < dirs.length; i++) {
        var d = dirs[i];
        var nx = cur.x + d.dx, ny = cur.y + d.dy, nk = key(nx, ny);
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
        q.push({ x: nx, y: ny });
      }
    }
    return null;
  }

  function paint() {
    canvas.width = PAD * 2 + state.width * CELL;
    canvas.height = PAD * 2 + state.height * CELL;
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    var x, y, k;
    for (y = 0; y < state.height; y++) {
      for (x = 0; x < state.width; x++) {
        var px = PAD + x * CELL, py = PAD + y * CELL;
        ctx.fillStyle = '#3a3a55';
        ctx.fillRect(px, py, CELL, CELL);
        ctx.strokeStyle = '#444466';
        ctx.strokeRect(px, py, CELL, CELL);
      }
    }
    for (k in state.walls) {
      var p1 = k.split(','); x = +p1[0]; y = +p1[1];
      ctx.fillStyle = '#4a4a6a';
      ctx.fillRect(PAD + x * CELL, PAD + y * CELL, CELL, CELL);
    }
    for (k in state.goals) {
      var p2 = k.split(','); x = +p2[0]; y = +p2[1];
      ctx.beginPath();
      ctx.arc(PAD + x * CELL + CELL / 2, PAD + y * CELL + CELL / 2, 6, 0, Math.PI * 2);
      ctx.fillStyle = '#e94560';
      ctx.fill();
    }
    for (k in state.boxes) {
      var p3 = k.split(','); x = +p3[0]; y = +p3[1];
      var on = !!state.goals[k];
      ctx.fillStyle = on ? '#2ecc71' : '#f39c12';
      ctx.fillRect(PAD + x * CELL + 4, PAD + y * CELL + 4, CELL - 8, CELL - 8);
    }
    ctx.beginPath();
    ctx.arc(
      PAD + state.player.x * CELL + CELL / 2,
      PAD + state.player.y * CELL + CELL / 2,
      CELL * 0.35, 0, Math.PI * 2
    );
    ctx.fillStyle = '#3498db';
    ctx.fill();
    hud.textContent = '步数：' + state.moves + (state.won ? ' · 过关！' : '');
  }

  function reset() {
    state = fromRows(LEVEL);
    paint();
  }

  document.addEventListener('keydown', function (e) {
    var map = {
      ArrowUp: [0, -1], ArrowDown: [0, 1], ArrowLeft: [-1, 0], ArrowRight: [1, 0],
      w: [0, -1], s: [0, 1], a: [-1, 0], d: [1, 0],
      W: [0, -1], S: [0, 1], A: [-1, 0], D: [1, 0],
    };
    if (e.key === 'z' || e.key === 'Z') { e.preventDefault(); undo(); return; }
    if (e.key === 'r' || e.key === 'R') { e.preventDefault(); reset(); return; }
    var d = map[e.key];
    if (d) { e.preventDefault(); tryMove(d[0], d[1]); }
  });

  canvas.addEventListener('click', function (e) {
    if (!state || state.won) return;
    var rect = canvas.getBoundingClientRect();
    var gx = Math.floor((e.clientX - rect.left - PAD) / CELL);
    var gy = Math.floor((e.clientY - rect.top - PAD) / CELL);
    if (gx < 0 || gy < 0 || gx >= state.width || gy >= state.height) return;
    var gk = key(gx, gy);
    if (state.boxes[gk]) {
      var dx = gx - state.player.x, dy = gy - state.player.y;
      if (Math.abs(dx) + Math.abs(dy) === 1) tryMove(dx, dy);
      return;
    }
    if (!state.walls[gk] && !state.boxes[gk]) {
      var path = findPath(gx, gy);
      if (path) {
        for (var i = 0; i < path.length; i++) {
          tryMove(path[i].dx, path[i].dy);
          if (state.won) break;
        }
      }
    }
  });

  reset();
})();
