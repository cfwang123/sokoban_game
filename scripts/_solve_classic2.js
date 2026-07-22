// 经典关：星形 16 箱
const rows = [
  '#######',
  '#*.*.*#',
  '#.$$$.#',
  '#*$@$*#',
  '#.$$$.#',
  '#*.*.*#',
  '#######',
];
console.log(rows.join('\n'));

const W = new Set(), G = new Set(), B = new Set();
let P = null;
for (let y = 0; y < rows.length; y++) {
  for (let x = 0; x < rows[y].length; x++) {
    const c = rows[y][x], k = x + ',' + y;
    if (c === '#') W.add(k);
    else if (c === '.') G.add(k);
    else if (c === '$') B.add(k);
    else if (c === '*') { B.add(k); G.add(k); }
    else if (c === '@') P = { x, y };
    else if (c === '+') { P = { x, y }; G.add(k); }
  }
}
console.log('boxes', B.size, 'goals', G.size, 'player', P);

// reverse dead squares
const floors = [];
for (let y = 0; y < rows.length; y++)
  for (let x = 0; x < rows[y].length; x++) {
    const k = x + ',' + y;
    if (!W.has(k)) floors.push(k);
  }
const DIRS = [[0, -1], [0, 1], [-1, 0], [1, 0]];
const alive = new Set(G);
const qq = [...G];
for (let i = 0; i < qq.length; i++) {
  const [x, y] = qq[i].split(',').map(Number);
  for (const [dx, dy] of DIRS) {
    const Fx = x - dx, Fy = y - dy;
    const Px = x - 2 * dx, Py = y - 2 * dy;
    const fk = Fx + ',' + Fy, pk = Px + ',' + Py;
    if (W.has(fk) || W.has(pk)) continue;
    if (!alive.has(fk) && !W.has(fk)) { alive.add(fk); qq.push(fk); }
  }
}
const dead = new Set();
for (const c of floors) {
  if (G.has(c)) continue;
  if (!alive.has(c)) { dead.add(c); continue; }
  const [x, y] = c.split(',').map(Number);
  const u = W.has(x + ',' + (y - 1)), d = W.has(x + ',' + (y + 1));
  const l = W.has((x - 1) + ',' + y), r = W.has((x + 1) + ',' + y);
  if ((u && l) || (u && r) || (d && l) || (d && r)) dead.add(c);
}
console.log('dead cells', dead.size, 'alive', alive.size);

// neighbors
const neigh = {};
for (const c of floors) {
  const [x, y] = c.split(',').map(Number);
  neigh[c] = [];
  for (const [dx, dy] of DIRS) {
    const nk = (x + dx) + ',' + (y + dy);
    if (!W.has(nk)) neigh[c].push(nk);
  }
}

function reach(px, py, boxes) {
  const s = new Set();
  const q = [px + ',' + py];
  s.add(q[0]);
  for (let i = 0; i < q.length; i++) {
    for (const n of neigh[q[i]]) {
      if (!s.has(n) && !boxes.has(n)) { s.add(n); q.push(n); }
    }
  }
  return s;
}

function stateKey(px, py, boxes) {
  // normalize by min reach
  const r = reach(px, py, boxes);
  let minR = Infinity;
  for (const c of r) {
    const [x, y] = c.split(',').map(Number);
    const id = y * 10 + x;
    if (id < minR) minR = id;
  }
  return minR + '|' + [...boxes].sort().join(';');
}

function isWin(boxes) {
  for (const b of boxes) if (!G.has(b)) return false;
  return true;
}

function check2x2(boxes, moved) {
  const [mx, my] = moved.split(',').map(Number);
  for (const [ox, oy] of [[0, 0], [-1, 0], [0, -1], [-1, -1]]) {
    let all = true, anyG = false;
    for (const [dx, dy] of [[0, 0], [1, 0], [0, 1], [1, 1]]) {
      const k = (mx + ox + dx) + ',' + (my + oy + dy);
      if (W.has(k) || !boxes.has(k)) { all = false; break; }
      if (G.has(k)) anyG = true;
    }
    if (all && !anyG) return true;
  }
  return false;
}

// A* weighted / greedy
class MinHeap {
  constructor() { this.a = []; }
  push(n) {
    const a = this.a; a.push(n);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (a[p].f <= a[i].f) break;
      [a[p], a[i]] = [a[i], a[p]]; i = p;
    }
  }
  pop() {
    const a = this.a;
    if (a.length === 1) return a.pop();
    const t = a[0]; a[0] = a.pop();
    let i = 0;
    for (;;) {
      let s = i, l = 2 * i + 1, r = 2 * i + 2;
      if (l < a.length && a[l].f < a[s].f) s = l;
      if (r < a.length && a[r].f < a[s].f) s = r;
      if (s === i) break;
      [a[i], a[s]] = [a[s], a[i]]; i = s;
    }
    return t;
  }
  get size() { return this.a.length; }
}

const goalDist = {};
for (const c of floors) {
  const [x, y] = c.split(',').map(Number);
  let md = Infinity;
  for (const g of G) {
    const [gx, gy] = g.split(',').map(Number);
    md = Math.min(md, Math.abs(x - gx) + Math.abs(y - gy));
  }
  goalDist[c] = md;
}

function h(boxes) {
  let s = 0;
  for (const b of boxes) s += goalDist[b];
  return s;
}

const DCH = ['u', 'd', 'l', 'r'];
const TL = +(process.argv[2] || 120000);
const T0 = Date.now();
const pq = new MinHeap();
const startBoxes = new Set(B);
const startH = h(startBoxes);
pq.push({ px: P.x, py: P.y, boxes: startBoxes, path: '', g: 0, f: startH });
const visited = new Set([stateKey(P.x, P.y, startBoxes)]);
let nodes = 0, expansions = 0;
let legal0 = 0;

// count start moves
{
  const r = reach(P.x, P.y, startBoxes);
  for (const bk of startBoxes) {
    const [bx, by] = bk.split(',').map(Number);
    for (let di = 0; di < 4; di++) {
      const [dx, dy] = DIRS[di];
      const tk = (bx + dx) + ',' + (by + dy);
      const fk = (bx - dx) + ',' + (by - dy);
      if (W.has(tk) || startBoxes.has(tk)) continue;
      if (!r.has(fk)) continue;
      if (dead.has(tk)) continue;
      legal0++;
    }
  }
  console.log('start legal pushes', legal0, 'startH', startH);
}

const W_ASTAR = 3;

while (pq.size > 0) {
  if ((expansions & 1023) === 0 && Date.now() - T0 > TL) {
    console.log('TIMEOUT', Date.now() - T0, 'nodes', nodes, 'exp', expansions, 'vis', visited.size);
    process.exit(1);
  }
  const cur = pq.pop();
  expansions++;
  if (isWin(cur.boxes)) {
    console.log('SOLVED in', Date.now() - T0, 'ms  pushes', cur.path.length);
    console.log('path:', cur.path);
    console.log('nodes', nodes, 'expansions', expansions);
    process.exit(0);
  }
  const r = reach(cur.px, cur.py, cur.boxes);
  for (const bk of cur.boxes) {
    const [bx, by] = bk.split(',').map(Number);
    for (let di = 0; di < 4; di++) {
      const [dx, dy] = DIRS[di];
      const tk = (bx + dx) + ',' + (by + dy);
      const fk = (bx - dx) + ',' + (by - dy);
      if (W.has(tk) || cur.boxes.has(tk)) continue;
      if (!r.has(fk)) continue;
      if (dead.has(tk)) continue;
      const nb = new Set(cur.boxes);
      nb.delete(bk); nb.add(tk);
      if (check2x2(nb, tk)) continue;
      const npx = bx, npy = by;
      const sk = stateKey(npx, npy, nb);
      if (visited.has(sk)) continue;
      visited.add(sk);
      const nh = h(nb);
      nodes++;
      pq.push({
        px: npx, py: npy, boxes: nb,
        path: cur.path + DCH[di],
        g: cur.g + 1,
        f: cur.g + 1 + W_ASTAR * nh
      });
    }
  }
}
console.log('exhausted', nodes, expansions);
process.exit(1);
