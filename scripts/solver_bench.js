// Sokoban solver benchmark - find hard levels & measure solve time
const fs = require('fs');
const path = require('path');

const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'levels.json'), 'utf8'));

// ========== Baseline A* (from solve_levels.js) ==========
function buildBaseline(levelRows) {
  const W = new Set(), G = new Set();
  for (let y = 0; y < levelRows.length; y++)
    for (let x = 0; x < levelRows[y].length; x++) {
      const c = levelRows[y][x], k = x + ',' + y;
      if (c === '#') W.add(k);
      else if (c === '.' || c === '*' || c === '+') G.add(k);
    }

  const goalDist = {};
  const neighbors = {};
  const allCells = [];
  for (let y = 0; y < levelRows.length; y++)
    for (let x = 0; x < levelRows[y].length; x++) {
      const k = x + ',' + y;
      if (W.has(k)) continue;
      allCells.push(k);
      let md = Infinity;
      for (const g of G) {
        const [gx, gy] = g.split(',').map(Number);
        md = Math.min(md, Math.abs(x - gx) + Math.abs(y - gy));
      }
      goalDist[k] = md;
      const ns = [];
      for (const [dx, dy] of [[0, -1], [0, 1], [-1, 0], [1, 0]]) {
        const nk = (x + dx) + ',' + (y + dy);
        if (!W.has(nk)) ns.push(nk);
      }
      neighbors[k] = ns;
    }

  const deadCells = new Set();
  for (const cell of allCells) {
    if (G.has(cell)) continue;
    const [x, y] = cell.split(',').map(Number);
    const u = W.has(x + ',' + (y - 1)), d = W.has(x + ',' + (y + 1));
    const l = W.has((x - 1) + ',' + y), r = W.has((x + 1) + ',' + y);
    if ((u && l) || (u && r) || (d && l) || (d && r)) { deadCells.add(cell); continue; }
    if ((u && d) && (l || r)) { deadCells.add(cell); continue; }
    if ((l && r) && (u || d)) { deadCells.add(cell); continue; }
  }

  function reachable(px, py, boxes) {
    const seen = new Set();
    const q = [px + ',' + py];
    seen.add(q[0]);
    for (let i = 0; i < q.length; i++) {
      for (const nk of neighbors[q[i]]) {
        if (!seen.has(nk) && !boxes.has(nk)) { seen.add(nk); q.push(nk); }
      }
    }
    return seen;
  }

  function check2x2(bx, by, boxes) {
    for (const [dx, dy] of [[0, 0], [-1, 0], [0, -1], [-1, -1]]) {
      const c1 = (bx + dx) + ',' + (by + dy);
      const c2 = (bx + dx + 1) + ',' + (by + dy);
      const c3 = (bx + dx) + ',' + (by + dy + 1);
      const c4 = (bx + dx + 1) + ',' + (by + dy + 1);
      if (boxes.has(c1) && boxes.has(c2) && boxes.has(c3) && boxes.has(c4)) {
        if (!G.has(c1) && !G.has(c2) && !G.has(c3) && !G.has(c4)) return true;
      }
    }
    return false;
  }

  function stateKey(px, py, boxes) {
    return px + ',' + py + '|' + Array.from(boxes).sort().join(';');
  }

  class MinHeap {
    constructor() { this.heap = []; }
    push(node) {
      this.heap.push(node);
      let i = this.heap.length - 1;
      while (i > 0) {
        const p = (i - 1) >> 1;
        if (this.heap[p].f <= this.heap[i].f) break;
        [this.heap[p], this.heap[i]] = [this.heap[i], this.heap[p]];
        i = p;
      }
    }
    pop() {
      if (this.heap.length === 1) return this.heap.pop();
      const top = this.heap[0];
      this.heap[0] = this.heap.pop();
      let i = 0, n = this.heap.length;
      while (true) {
        let s = i; const l = i * 2 + 1, r = i * 2 + 2;
        if (l < n && this.heap[l].f < this.heap[s].f) s = l;
        if (r < n && this.heap[r].f < this.heap[s].f) s = r;
        if (s === i) break;
        [this.heap[i], this.heap[s]] = [this.heap[s], this.heap[i]];
        i = s;
      }
      return top;
    }
    get size() { return this.heap.length; }
  }

  const dirs = [[0, -1, 'u'], [0, 1, 'd'], [-1, 0, 'l'], [1, 0, 'r']];
  const W_ASTAR = 2;

  return function solve(timeLimit) {
    const B = new Set();
    let P2 = null;
    for (let y = 0; y < levelRows.length; y++)
      for (let x = 0; x < levelRows[y].length; x++) {
        const c = levelRows[y][x], k = x + ',' + y;
        if (c === '$' || c === '*') B.add(k);
        if (c === '@' || c === '+') P2 = { x, y };
      }

    let startH = 0;
    for (const b of B) startH += goalDist[b];
    const pq = new MinHeap();
    pq.push({ px: P2.x, py: P2.y, boxes: new Set(B), path: [], f: W_ASTAR * startH, g: 0, h: startH });
    const visited = new Set([stateKey(P2.x, P2.y, B)]);
    const T0 = Date.now();
    let nodes = 0;

    while (pq.size > 0) {
      if (Date.now() - T0 > timeLimit) return { ok: false, nodes, ms: Date.now() - T0 };
      const cur = pq.pop();
      nodes++;
      let won = true;
      for (const b of cur.boxes) { if (!G.has(b)) { won = false; break; } }
      if (won) return { ok: true, path: cur.path.join(''), nodes, ms: Date.now() - T0 };

      const r = reachable(cur.px, cur.py, cur.boxes);
      for (const bk of cur.boxes) {
        const [bx, by] = bk.split(',').map(Number);
        for (const [dx, dy, dn] of dirs) {
          const tk = (bx + dx) + ',' + (by + dy);
          const fk = (bx - dx) + ',' + (by - dy);
          if (W.has(tk) || cur.boxes.has(tk)) continue;
          if (!r.has(fk)) continue;
          if (deadCells.has(tk)) continue;
          const nb = new Set(cur.boxes);
          nb.delete(bk); nb.add(tk);
          if (check2x2(bx + dx, by + dy, nb)) continue;
          const npx = +fk.split(',')[0], npy = +fk.split(',')[1];
          const nk = stateKey(npx, npy, nb);
          if (visited.has(nk)) continue;
          visited.add(nk);
          const nh = cur.h - goalDist[bk] + goalDist[tk];
          pq.push({ px: npx, py: npy, boxes: nb, path: cur.path.concat([dn]), f: cur.g + 1 + W_ASTAR * nh, g: cur.g + 1, h: nh });
        }
      }
    }
    return { ok: false, nodes, ms: Date.now() - T0 };
  };
}

// Benchmark: test levels without solution, and some hard ones with many boxes
const candidates = data.filter(l => !l.solution);
// Also include levels with many boxes that have solutions (for hardness)
const byBoxes = data.map(l => {
  let b = 0;
  l.puzzle.forEach(r => { for (const c of r) if (c === '$' || c === '*') b++; });
  return { level: l, boxes: b };
}).sort((a, b) => b.boxes - a.boxes);

console.log('No solution:', candidates.length);
console.log('Top hard by boxes:');
byBoxes.slice(0, 15).forEach(x => console.log(`  id=${x.level.id} ${x.level.name} boxes=${x.boxes} sol=${!!x.level.solution}`));

const TIME = 5000;
// Test unsolved first (sample of medium-hard by box count)
const unsolvedByBoxes = candidates.map(l => {
  let b = 0;
  l.puzzle.forEach(r => { for (const c of r) if (c === '$' || c === '*') b++; });
  return { level: l, boxes: b };
}).sort((a, b) => a.boxes - b.boxes);

console.log('\n=== Baseline A* on unsolved (easiest first, stop after finding hard ones) ===\n');

const hard = [];
let tested = 0;
for (const { level, boxes } of unsolvedByBoxes) {
  if (boxes < 4) continue; // skip trivial
  if (tested >= 40 && hard.length >= 3) break;
  tested++;
  const solve = buildBaseline(level.puzzle);
  const r = solve(TIME);
  const status = r.ok ? `OK ${r.ms}ms pushes=${r.path.length}` : `FAIL ${r.ms}ms nodes=${r.nodes}`;
  console.log(`[${tested}] id=${level.id} ${level.name} boxes=${boxes}: ${status}`);
  if (!r.ok) hard.push({ id: level.id, name: level.name, boxes, nodes: r.nodes });
  if (r.ok && r.ms > 2000) hard.push({ id: level.id, name: level.name, boxes, nodes: r.nodes, ms: r.ms, slow: true });
}

console.log('\nHard levels (>5s or slow):');
hard.forEach(h => console.log(JSON.stringify(h)));
