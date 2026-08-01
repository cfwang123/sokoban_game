// 推箱子核心（微信小游戏 / 浏览器同源逻辑）
function parseLevel(rows, index) {
  const walls = new Set(), goals = new Set(), boxes = new Set();
  let player = { x: 0, y: 0 }, maxX = 0, maxY = 0;
  for (let y = 0; y < rows.length; y++) {
    maxY = y;
    const row = rows[y];
    for (let x = 0; x < row.length; x++) {
      maxX = Math.max(maxX, x);
      const k = x + ',' + y, ch = row[x];
      if (ch === '#') walls.add(k);
      else if (ch === '.') goals.add(k);
      else if (ch === '$') boxes.add(k);
      else if (ch === '*') { boxes.add(k); goals.add(k); }
      else if (ch === '@') player = { x, y };
      else if (ch === '+') { player = { x, y }; goals.add(k); }
    }
  }
  return { walls, goals, boxes, player, moves: 0, won: false, history: [], levelIndex: index, width: maxX + 1, height: maxY + 1 };
}

function tryMove(s, dx, dy) {
  if (s.won) return false;
  const nx = s.player.x + dx, ny = s.player.y + dy, nk = nx + ',' + ny;
  if (s.walls.has(nk)) return false;
  if (s.boxes.has(nk)) {
    const bx = nx + dx, by = ny + dy, bk = bx + ',' + by;
    if (s.walls.has(bk) || s.boxes.has(bk)) return false;
    s.history.push({ px: s.player.x, py: s.player.y, from: nk, to: bk, push: true });
    s.boxes.delete(nk); s.boxes.add(bk);
    s.player.x = nx; s.player.y = ny; s.moves++; checkWin(s); return true;
  }
  s.history.push({ px: s.player.x, py: s.player.y, push: false });
  s.player.x = nx; s.player.y = ny; return true;
}

function undo(s) {
  if (s.won || !s.history.length) return;
  let e;
  while (s.history.length) {
    e = s.history.pop();
    if (e.push) break;
    s.player.x = e.px; s.player.y = e.py;
  }
  if (!e || !e.push) return;
  s.player.x = e.px; s.player.y = e.py;
  s.boxes.delete(e.to); s.boxes.add(e.from);
  if (s.moves > 0) s.moves--;
  s.won = false;
}

function checkWin(s) {
  for (const b of s.boxes) if (!s.goals.has(b)) { s.won = false; return; }
  s.won = true;
}

function findPath(s, tx, ty) {
  const start = s.player.x + ',' + s.player.y, target = tx + ',' + ty;
  if (start === target) return [];
  const blocked = new Set(s.walls); for (const b of s.boxes) blocked.add(b);
  const q = [{ x: s.player.x, y: s.player.y }], vis = new Set([start]), parent = new Map();
  const dirs = [[0, -1], [0, 1], [-1, 0], [1, 0]];
  while (q.length) {
    const c = q.shift(), ck = c.x + ',' + c.y;
    for (const [dx, dy] of dirs) {
      const nx = c.x + dx, ny = c.y + dy, nk = nx + ',' + ny;
      if (blocked.has(nk) || vis.has(nk)) continue;
      vis.add(nk); parent.set(nk, { from: ck, dx, dy });
      if (nk === target) {
        const path = []; let p = nk;
        while (p !== start) { const i = parent.get(p); path.unshift([i.dx, i.dy]); p = i.from; }
        return path;
      }
      q.push({ x: nx, y: ny });
    }
  }
  return null;
}

module.exports = { parseLevel, tryMove, undo, findPath };
