/**
 * 生成完整玩家路径（含走路），写入 levels.json 并同步各版本
 */
const fs = require('fs');
const path = require('path');

const puzzle = [
  '#######',
  '#. . .#',
  '# $$$ #',
  '#.$@$.#',
  '# $$$ #',
  '#. . .#',
  '#######',
];

// 已验证的 20 推最优序列（BFS）
const PUSHES = 'ulrdlurdurudldrlruld';

// ---- parse ----
const W = new Set(), G = new Set(), B0 = new Set();
let P0 = null;
for (let y = 0; y < puzzle.length; y++) {
  for (let x = 0; x < puzzle[y].length; x++) {
    const c = puzzle[y][x], k = x + ',' + y;
    if (c === '#') W.add(k);
    else if (c === '.') G.add(k);
    else if (c === '$') B0.add(k);
    else if (c === '*') { B0.add(k); G.add(k); }
    else if (c === '@') P0 = { x, y };
    else if (c === '+') { P0 = { x, y }; G.add(k); }
  }
}

const DIRS = { u: [0, -1], d: [0, 1], l: [-1, 0], r: [1, 0] };
const DLIST = [['u', 0, -1], ['d', 0, 1], ['l', -1, 0], ['r', 1, 0]];
const OPP = { u: 'd', d: 'u', l: 'r', r: 'l' };

function reachable(px, py, boxes) {
  const s = new Set([px + ',' + py]);
  const q = [[px, py]];
  const parent = new Map(); // key -> {pk, ch}
  parent.set(px + ',' + py, null);
  for (let i = 0; i < q.length; i++) {
    const [x, y] = q[i];
    for (const [ch, dx, dy] of DLIST) {
      const nx = x + dx, ny = y + dy, k = nx + ',' + ny;
      if (W.has(k) || boxes.has(k) || s.has(k)) continue;
      s.add(k); q.push([nx, ny]);
      parent.set(k, { pk: x + ',' + y, ch });
    }
  }
  return { set: s, parent };
}

function walkPath(parent, fromKey, toKey) {
  // reconstruct path from fromKey to toKey using parent of BFS from fromKey
  // parent maps node -> {pk, ch} where ch is move TO this node from pk
  if (fromKey === toKey) return '';
  const steps = [];
  let cur = toKey;
  while (cur !== fromKey) {
    const p = parent.get(cur);
    if (!p) return null;
    steps.push(p.ch);
    cur = p.pk;
  }
  steps.reverse();
  return steps.join('');
}

function isWin(boxes) {
  for (const b of boxes) if (!G.has(b)) return false;
  return true;
}

// ---- convert pushes to full player LURD (lowercase walk, uppercase push) ----
// Game uses toUpperCase so case doesn't matter; use mixed for readability: push = upper
function pushesToPlayerPath(pushStr) {
  let px = P0.x, py = P0.y;
  const boxes = new Set(B0);
  let full = '';

  for (let i = 0; i < pushStr.length; i++) {
    const ch = pushStr[i];
    const [dx, dy] = DIRS[ch];
    const { set: r, parent } = reachable(px, py, boxes);

    // find the box that the solver would push: after previous push player is on old box cell
    // match: any box pushable in dir ch where player can reach from-cell
    // Prefer unique; if multiple, the sequence from BFS detailed moves is better
    // Use detailed replay matching from known moves list
    const cands = [];
    for (const bk of boxes) {
      const [bx, by] = bk.split(',').map(Number);
      const tk = (bx + dx) + ',' + (by + dy);
      const fk = (bx - dx) + ',' + (by - dy);
      if (W.has(tk) || boxes.has(tk)) continue;
      if (!r.has(fk)) continue;
      cands.push({ bk, bx, by, tk, fk });
    }
    if (cands.length === 0) throw new Error('no push at ' + i + ' ' + ch);

    // pick candidate with shortest walk from player
    cands.sort((a, b) => {
      const wa = walkPath(parent, px + ',' + py, a.fk);
      const wb = walkPath(parent, px + ',' + py, b.fk);
      return (wa || 'xxxxxxxxxx').length - (wb || 'xxxxxxxxxx').length;
    });
    const c = cands[0];
    const walk = walkPath(parent, px + ',' + py, c.fk);
    if (walk === null) throw new Error('no walk at ' + i);
    full += walk; // lowercase walks
    full += ch.toUpperCase(); // uppercase push
    boxes.delete(c.bk);
    boxes.add(c.tk);
    px = c.bx; py = c.by;
  }
  if (!isWin(boxes)) throw new Error('not win after path');
  return full;
}

// Better: use recorded detailed moves from BFS with exact box targets
function solveWithMoves() {
  // BFS for push-optimal, store exact moves
  function stateKey(px, py, boxes) {
    const { set: r } = reachable(px, py, boxes);
    let min = null;
    for (const c of r) if (min === null || c < min) min = c;
    return min + '|' + [...boxes].sort().join(';');
  }
  const dead = new Set(); // none for this level
  const q = [{ px: P0.x, py: P0.y, boxes: new Set(B0), moves: [] }];
  let qi = 0;
  const visited = new Set([stateKey(P0.x, P0.y, B0)]);
  while (qi < q.length) {
    const cur = q[qi++];
    if (isWin(cur.boxes)) return cur.moves;
    const { set: r } = reachable(cur.px, cur.py, cur.boxes);
    for (const bk of cur.boxes) {
      const [bx, by] = bk.split(',').map(Number);
      for (const [ch, dx, dy] of DLIST) {
        const tk = (bx + dx) + ',' + (by + dy);
        const fk = (bx - dx) + ',' + (by - dy);
        if (W.has(tk) || cur.boxes.has(tk)) continue;
        if (!r.has(fk)) continue;
        const nb = new Set(cur.boxes);
        nb.delete(bk); nb.add(tk);
        const sk = stateKey(bx, by, nb);
        if (visited.has(sk)) continue;
        visited.add(sk);
        q.push({
          px: bx, py: by, boxes: nb,
          moves: cur.moves.concat([{ ch, from: bk, to: tk, playerFrom: fk }])
        });
      }
    }
  }
  throw new Error('no solution');
}

function movesToPlayerPath(moves) {
  let px = P0.x, py = P0.y;
  const boxes = new Set(B0);
  let full = '';
  for (const m of moves) {
    const { set: r, parent } = reachable(px, py, boxes);
    if (!r.has(m.playerFrom)) throw new Error('cannot reach ' + m.playerFrom);
    const walk = walkPath(parent, px + ',' + py, m.playerFrom);
    if (walk === null) throw new Error('no walk');
    full += walk;
    full += m.ch.toUpperCase();
    boxes.delete(m.from);
    boxes.add(m.to);
    px = +m.from.split(',')[0];
    py = +m.from.split(',')[1];
  }
  if (!isWin(boxes)) throw new Error('not win');
  // verify replay
  px = P0.x; py = P0.y;
  const boxes2 = new Set(B0);
  for (const ch of full) {
    const lower = ch.toLowerCase();
    const [dx, dy] = DIRS[lower];
    const nx = px + dx, ny = py + dy, nk = nx + ',' + ny;
    if (W.has(nk)) throw new Error('hit wall ' + ch);
    if (boxes2.has(nk)) {
      const bx = nx + dx, by = ny + dy, bk = bx + ',' + by;
      if (W.has(bk) || boxes2.has(bk)) throw new Error('bad push');
      boxes2.delete(nk); boxes2.add(bk);
    }
    px = nx; py = ny;
  }
  if (!isWin(boxes2)) throw new Error('replay fail');
  return full;
}

console.log('Solving for detailed moves...');
const moves = solveWithMoves();
console.log('pushes', moves.length);
const solution = movesToPlayerPath(moves);
console.log('full solution length', solution.length);
console.log('solution:', solution);

// ---- write levels.json ----
const root = path.join(__dirname, '..');
const jsonPath = path.join(root, 'levels.json');
const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

const newLevel = {
  id: null, // fill later
  name: 'Classic Star',
  puzzle: puzzle,
  solution: solution
};

// Replace broken id=-1 if present, else insert after first, or append
const idxNeg = data.findIndex(l => l.id === -1 || l.name === '-1 L');
if (idxNeg >= 0) {
  newLevel.id = data[idxNeg].id === -1 ? -1 : data[idxNeg].id;
  // use a proper id: keep -1 or use max+1
  // Prefer replacing the wrong star level with correct one under a good name
  newLevel.id = -1;
  data[idxNeg] = newLevel;
  console.log('Replaced level at index', idxNeg, 'id=-1');
} else {
  // insert as first playable-ish: use id -1 at front, or append with new id
  const maxId = Math.max(...data.map(l => l.id));
  newLevel.id = maxId + 1;
  data.push(newLevel);
  console.log('Appended level id', newLevel.id);
}

// Also ensure we don't have duplicate "Classic Star"
const stars = data.filter(l => l.name === 'Classic Star');
if (stars.length > 1) {
  // keep first
  let seen = false;
  for (let i = data.length - 1; i >= 0; i--) {
    if (data[i].name === 'Classic Star') {
      if (seen) data.splice(i, 1);
      else seen = true;
    }
  }
}

fs.writeFileSync(jsonPath, JSON.stringify(data, null, 2), 'utf8');
console.log('Wrote levels.json, total', data.length);

// sync c_app and sokoban_linux
for (const dir of ['c_app', 'sokoban_linux']) {
  const p = path.join(root, dir, 'levels.json');
  fs.writeFileSync(p, JSON.stringify(data, null, 2), 'utf8');
  console.log('Synced', p);
}

// generate levels_data.js for html apps
const items = data.map(d => ({
  name: d.name,
  puzzle: d.puzzle,
  solution: d.solution || ''
}));
const js = `// 自动生成 - 从 levels.json 转换\nwindow.LEVELS_DATA = ${JSON.stringify(items)};`;
for (const dir of ['html_app/js', 'html_3dapp/js']) {
  const p = path.join(root, dir, 'levels_data.js');
  fs.writeFileSync(p, js, 'utf8');
  console.log('Synced', p);
}

console.log('\nDone. Level "Classic Star" with solution verified.');
console.log('Pushes:', moves.map(m => m.ch).join(''));
console.log('Player path:', solution);
