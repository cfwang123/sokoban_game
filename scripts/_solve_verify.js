/**
 * 求解并严格回放验证
 */
const rows = [
  '#######',
  '#. . .#',
  '# $$$ #',
  '#.$@$.#',
  '# $$$ #',
  '#. . .#',
  '#######',
];

console.log('=== Level ===');
rows.forEach((r, i) => console.log(i + ': ' + JSON.stringify(r) + ' len=' + r.length));

// pad to uniform width
const maxW = Math.max(...rows.map(r => r.length));
const level = rows.map(r => r.padEnd(maxW, '#'));
level.forEach(r => console.log(r));

const W = new Set(), G = new Set(), B0 = new Set();
let P0 = null;
for (let y = 0; y < level.length; y++) {
  for (let x = 0; x < level[y].length; x++) {
    const c = level[y][x], k = x + ',' + y;
    if (c === '#') W.add(k);
    else if (c === '.') G.add(k);
    else if (c === '$') B0.add(k);
    else if (c === '*') { B0.add(k); G.add(k); }
    else if (c === '@') P0 = { x, y };
    else if (c === '+') { P0 = { x, y }; G.add(k); }
    // space = floor
  }
}
console.log('boxes', B0.size, 'goals', G.size, 'player', P0);
console.log('goals:', [...G].sort().join(' '));
console.log('boxes:', [...B0].sort().join(' '));

const DIRS = { u: [0, -1], d: [0, 1], l: [-1, 0], r: [1, 0] };
const DLIST = [['u', 0, -1], ['d', 0, 1], ['l', -1, 0], ['r', 1, 0]];

function isWin(boxes) {
  for (const b of boxes) if (!G.has(b)) return false;
  return true;
}

function reachable(px, py, boxes) {
  const s = new Set([px + ',' + py]);
  const q = [[px, py]];
  for (let i = 0; i < q.length; i++) {
    const [x, y] = q[i];
    for (const [, dx, dy] of DLIST) {
      const nx = x + dx, ny = y + dy, k = nx + ',' + ny;
      if (W.has(k) || boxes.has(k) || s.has(k)) continue;
      s.add(k); q.push([nx, ny]);
    }
  }
  return s;
}

function deadCell(k) {
  if (G.has(k)) return false;
  const [x, y] = k.split(',').map(Number);
  const u = W.has(x + ',' + (y - 1)), d = W.has(x + ',' + (y + 1));
  const l = W.has((x - 1) + ',' + y), r = W.has((x + 1) + ',' + y);
  if ((u && l) || (u && r) || (d && l) || (d && r)) return true;
  if (u && d && (l || r)) return true;
  if (l && r && (u || d)) return true;
  return false;
}

// reverse-BFS alive
const floors = [];
for (let y = 0; y < level.length; y++)
  for (let x = 0; x < level[y].length; x++) {
    const k = x + ',' + y;
    if (!W.has(k)) floors.push(k);
  }
const alive = new Set(G);
const aq = [...G];
for (let i = 0; i < aq.length; i++) {
  const [x, y] = aq[i].split(',').map(Number);
  for (const [, dx, dy] of DLIST) {
    const Fx = x - dx, Fy = y - dy;
    const Px = x - 2 * dx, Py = y - 2 * dy;
    const fk = Fx + ',' + Fy, pk = Px + ',' + Py;
    if (W.has(fk) || W.has(pk)) continue;
    if (!alive.has(fk)) { alive.add(fk); aq.push(fk); }
  }
}
const dead = new Set();
for (const c of floors) {
  if (G.has(c)) continue;
  if (!alive.has(c) || deadCell(c)) dead.add(c);
}
console.log('dead', dead.size);

function stateKey(px, py, boxes) {
  const r = reachable(px, py, boxes);
  let min = null;
  for (const c of r) {
    if (min === null || c < min) min = c;
  }
  return min + '|' + [...boxes].sort().join(';');
}

function h(boxes) {
  let s = 0;
  for (const b of boxes) {
    const [x, y] = b.split(',').map(Number);
    let md = Infinity;
    for (const g of G) {
      const [gx, gy] = g.split(',').map(Number);
      md = Math.min(md, Math.abs(x - gx) + Math.abs(y - gy));
    }
    s += md;
  }
  return s;
}

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

// --- solve: try multiple modes ---
function solve(mode, timeLimit) {
  const T0 = Date.now();
  const WA = mode === 'opt' ? 1 : mode === 'wastar' ? 2 : 0; // 0 = pure greedy f=h
  const pq = new MinHeap();
  const startH = h(B0);
  const f0 = mode === 'greedy' ? startH : startH; // g + WA*h below
  pq.push({ px: P0.x, py: P0.y, boxes: new Set(B0), path: '', g: 0, f: startH });
  const visited = new Map();
  visited.set(stateKey(P0.x, P0.y, B0), 0);
  let nodes = 0, exp = 0;

  while (pq.size > 0) {
    if ((exp & 511) === 0 && Date.now() - T0 > timeLimit) {
      return { ok: false, ms: Date.now() - T0, nodes, exp, visited: visited.size };
    }
    const cur = pq.pop();
    exp++;
    if (isWin(cur.boxes)) {
      return { ok: true, path: cur.path, pushes: cur.g, ms: Date.now() - T0, nodes, exp };
    }
    const r = reachable(cur.px, cur.py, cur.boxes);
    for (const bk of cur.boxes) {
      const [bx, by] = bk.split(',').map(Number);
      for (const [ch, dx, dy] of DLIST) {
        const tk = (bx + dx) + ',' + (by + dy);
        const fk = (bx - dx) + ',' + (by - dy);
        if (W.has(tk) || cur.boxes.has(tk)) continue;
        if (!r.has(fk)) continue;
        if (dead.has(tk)) continue;
        const nb = new Set(cur.boxes);
        nb.delete(bk); nb.add(tk);
        // 2x2
        let d22 = false;
        for (const [ox, oy] of [[0, 0], [-1, 0], [0, -1], [-1, -1]]) {
          let all = true, anyG = false;
          for (const [dx2, dy2] of [[0, 0], [1, 0], [0, 1], [1, 1]]) {
            const k2 = (bx + dx + ox + dx2) + ',' + (by + dy + oy + dy2);
            if (W.has(k2) || !nb.has(k2)) { all = false; break; }
            if (G.has(k2)) anyG = true;
          }
          if (all && !anyG) d22 = true;
        }
        if (d22) continue;

        const npx = bx, npy = by;
        const sk = stateKey(npx, npy, nb);
        const ng = cur.g + 1;
        const prev = visited.get(sk);
        if (prev !== undefined && prev <= ng) continue;
        visited.set(sk, ng);
        const nh = h(nb);
        const f = mode === 'greedy' ? nh : (ng + WA * nh);
        nodes++;
        pq.push({ px: npx, py: npy, boxes: nb, path: cur.path + ch, g: ng, f });
      }
    }
  }
  return { ok: false, ms: Date.now() - T0, nodes, exp, visited: visited.size };
}

// --- verify path (pushes only, player walks via BFS between pushes) ---
function verifyPushes(pushPath) {
  let px = P0.x, py = P0.y;
  const boxes = new Set(B0);
  const fullMoves = []; // actual player steps u/d/l/r

  for (let i = 0; i < pushPath.length; i++) {
    const ch = pushPath[i];
    const [dx, dy] = DIRS[ch];
    // find which box we can push in this direction from reachable area
    // The path stores push direction of the box; player must reach the cell behind the box
    // We need to find a box such that: player can reach (box-dir), and box can move to box+dir
    const r = reachable(px, py, boxes);
    let found = null;
    for (const bk of boxes) {
      const [bx, by] = bk.split(',').map(Number);
      const tk = (bx + dx) + ',' + (by + dy);
      const fk = (bx - dx) + ',' + (by - dy);
      if (W.has(tk) || boxes.has(tk)) continue;
      if (!r.has(fk)) continue;
      // path: player walks from (px,py) to (fk), then steps to (bx,by) pushing
      found = { bx, by, tk, fk };
      break; // if multiple, take first — might be ambiguous!
    }
    if (!found) {
      // try all boxes - collect all possible
      const cands = [];
      for (const bk of boxes) {
        const [bx, by] = bk.split(',').map(Number);
        const tk = (bx + dx) + ',' + (by + dy);
        const fk = (bx - dx) + ',' + (by - dy);
        if (W.has(tk) || boxes.has(tk)) continue;
        if (!r.has(fk)) continue;
        cands.push({ bx, by, tk, fk, bk });
      }
      if (cands.length === 0) {
        return { ok: false, reason: `push ${i} '${ch}' no legal box`, step: i };
      }
      // ambiguous: pick any (solver path is sequence of push dirs, may be ambiguous)
      found = cands[0];
      if (cands.length > 1) {
        // Prefer doesn't matter for win check if we follow solver's internal semantics:
        // After each push player is on old box cell. Reconstruct using that invariant.
      }
    }
  }

  // Better verify: replay using "player ends on pushed box origin"
  // Re-solve style: the path is only push directions as recorded by solver where
  // after each push player is at old box position. Between pushes player walks.
  // Ambiguity: multiple boxes pushable same dir. Store full reconstruction from solver instead.

  return { ok: null, note: 'use reconstruct verify below' };
}

// Reconstruct by re-running search that records box id, OR simulate uniquely when only one box matches.
function verifyUnique(pushPath) {
  let px = P0.x, py = P0.y;
  const boxes = new Set(B0);
  const log = [];

  for (let i = 0; i < pushPath.length; i++) {
    const ch = pushPath[i];
    const [dx, dy] = DIRS[ch];
    const r = reachable(px, py, boxes);
    const cands = [];
    for (const bk of boxes) {
      const [bx, by] = bk.split(',').map(Number);
      const tk = (bx + dx) + ',' + (by + dy);
      const fk = (bx - dx) + ',' + (by - dy);
      if (W.has(tk) || boxes.has(tk)) continue;
      if (!r.has(fk)) continue;
      cands.push({ bk, bx, by, tk, fk });
    }
    if (cands.length === 0) {
      return { ok: false, reason: `step ${i} push ${ch}: no box`, boxes: [...boxes], player: [px, py] };
    }
    // If ambiguous, the solver used player-at-previous-box: we need the path that matches
    // continuous play. Try each candidate DFS-style? For short paths try first, if fail try others.
    // Actually standard: expand all cands - for verification of "is there a walk consistent with this push string"
    // Use BFS on (stepIndex, state) - too heavy.
    // Simpler: when ambiguous pick candidate where fk is closest to player (min walk).
    cands.sort((a, b) => {
      const da = Math.abs(a.fk.split(',')[0] - px) + Math.abs(a.fk.split(',')[1] - py);
      const db = Math.abs(b.fk.split(',')[0] - px) + Math.abs(b.fk.split(',')[1] - py);
      return da - db;
    });
    const c = cands[0];
    boxes.delete(c.bk);
    boxes.add(c.tk);
    px = c.bx; py = c.by;
    log.push(`${ch}: box ${c.bk} -> ${c.tk}`);
  }
  const won = isWin(boxes);
  return { ok: won, log, boxes: [...boxes].sort(), goals: [...G].sort() };
}

// Full path search storing parent pointers with box+dir
function solveDetailed(timeLimit) {
  const T0 = Date.now();
  const pq = new MinHeap();
  pq.push({ px: P0.x, py: P0.y, boxes: new Set(B0), path: '', moves: [], g: 0, f: h(B0) });
  const visited = new Map();
  visited.set(stateKey(P0.x, P0.y, B0), 0);
  let nodes = 0, exp = 0;

  while (pq.size > 0) {
    if ((exp & 511) === 0 && Date.now() - T0 > timeLimit) break;
    const cur = pq.pop();
    exp++;
    if (isWin(cur.boxes)) {
      return {
        ok: true, path: cur.path, moves: cur.moves, pushes: cur.g,
        ms: Date.now() - T0, nodes, exp
      };
    }
    const r = reachable(cur.px, cur.py, cur.boxes);
    for (const bk of cur.boxes) {
      const [bx, by] = bk.split(',').map(Number);
      for (const [ch, dx, dy] of DLIST) {
        const tk = (bx + dx) + ',' + (by + dy);
        const fk = (bx - dx) + ',' + (by - dy);
        if (W.has(tk) || cur.boxes.has(tk)) continue;
        if (!r.has(fk)) continue;
        if (dead.has(tk)) continue;
        const nb = new Set(cur.boxes);
        nb.delete(bk); nb.add(tk);
        let d22 = false;
        for (const [ox, oy] of [[0, 0], [-1, 0], [0, -1], [-1, -1]]) {
          let all = true, anyG = false;
          for (const [dx2, dy2] of [[0, 0], [1, 0], [0, 1], [1, 1]]) {
            const k2 = (bx + dx + ox + dx2) + ',' + (by + dy + oy + dy2);
            if (W.has(k2) || !nb.has(k2)) { all = false; break; }
            if (G.has(k2)) anyG = true;
          }
          if (all && !anyG) d22 = true;
        }
        if (d22) continue;
        const sk = stateKey(bx, by, nb);
        const ng = cur.g + 1;
        const prev = visited.get(sk);
        if (prev !== undefined && prev <= ng) continue;
        visited.set(sk, ng);
        nodes++;
        const nh = h(nb);
        // A* weight 1 for shorter, also try greedy
        pq.push({
          px: bx, py: by, boxes: nb,
          path: cur.path + ch,
          moves: cur.moves.concat([{ ch, from: bk, to: tk, playerFrom: fk }]),
          g: ng, f: ng + 2 * nh
        });
      }
    }
  }
  return { ok: false, ms: Date.now() - T0, nodes, exp };
}

function replayMoves(moves) {
  let px = P0.x, py = P0.y;
  const boxes = new Set(B0);
  for (let i = 0; i < moves.length; i++) {
    const m = moves[i];
    const r = reachable(px, py, boxes);
    if (!r.has(m.playerFrom)) {
      return { ok: false, reason: `move ${i}: player cannot reach ${m.playerFrom}`, i };
    }
    if (!boxes.has(m.from)) {
      return { ok: false, reason: `move ${i}: no box at ${m.from}`, i };
    }
    if (boxes.has(m.to) || W.has(m.to)) {
      return { ok: false, reason: `move ${i}: blocked ${m.to}`, i };
    }
    // walk player to playerFrom then push
    boxes.delete(m.from);
    boxes.add(m.to);
    px = m.from.split(',')[0] - 0;
    py = m.from.split(',')[1] - 0;
  }
  return { ok: isWin(boxes), boxes: [...boxes].sort() };
}

function printBoard(px, py, boxes) {
  for (let y = 0; y < level.length; y++) {
    let line = '';
    for (let x = 0; x < level[y].length; x++) {
      const k = x + ',' + y;
      if (W.has(k)) line += '#';
      else if (px === x && py === y) line += G.has(k) ? '+' : '@';
      else if (boxes.has(k)) line += G.has(k) ? '*' : '$';
      else if (G.has(k)) line += '.';
      else line += ' ';
    }
    console.log(line);
  }
}

console.log('\n=== Solving (detailed A*) ===');
const r = solveDetailed(30000);
if (!r.ok) {
  console.log('FAILED', r);
  // try pure greedy
  console.log('\n=== Greedy ===');
  const g = solve('greedy', 30000);
  console.log(g);
  if (g.ok) {
    const v = verifyUnique(g.path);
    console.log('verifyUnique', v);
  }
  process.exit(1);
}

console.log(`SOLVED in ${r.ms}ms  pushes=${r.pushes}  nodes=${r.nodes}`);
console.log('push sequence (LURD):', r.path);
console.log('\nDetailed moves:');
r.moves.forEach((m, i) => {
  console.log(`  ${i + 1}. push ${m.ch}: box ${m.from} -> ${m.to} (player walked to ${m.playerFrom})`);
});

const rep = replayMoves(r.moves);
console.log('\n=== Replay verification ===');
console.log(rep.ok ? 'VALID SOLUTION ✓' : 'INVALID ✗', rep);

if (rep.ok) {
  console.log('\nFinal board:');
  // rebuild final
  let px = P0.x, py = P0.y;
  const boxes = new Set(B0);
  for (const m of r.moves) {
    boxes.delete(m.from); boxes.add(m.to);
    px = +m.from.split(',')[0]; py = +m.from.split(',')[1];
  }
  printBoard(px, py, boxes);
}

// Also BFS for push-optimal (shorter) if small enough
console.log('\n=== Push-optimal BFS (may be slow) ===');
function solveBFS(timeLimit) {
  const T0 = Date.now();
  const q = [{ px: P0.x, py: P0.y, boxes: new Set(B0), path: '', moves: [] }];
  let qi = 0;
  const visited = new Set([stateKey(P0.x, P0.y, B0)]);
  let exp = 0;
  while (qi < q.length) {
    if ((exp & 1023) === 0 && Date.now() - T0 > timeLimit) {
      return { ok: false, ms: Date.now() - T0, exp, queue: q.length };
    }
    const cur = q[qi++];
    exp++;
    if (isWin(cur.boxes)) {
      return { ok: true, path: cur.path, moves: cur.moves, pushes: cur.path.length, ms: Date.now() - T0, exp };
    }
    const rch = reachable(cur.px, cur.py, cur.boxes);
    for (const bk of cur.boxes) {
      const [bx, by] = bk.split(',').map(Number);
      for (const [ch, dx, dy] of DLIST) {
        const tk = (bx + dx) + ',' + (by + dy);
        const fk = (bx - dx) + ',' + (by - dy);
        if (W.has(tk) || cur.boxes.has(tk)) continue;
        if (!rch.has(fk)) continue;
        if (dead.has(tk)) continue;
        const nb = new Set(cur.boxes);
        nb.delete(bk); nb.add(tk);
        const sk = stateKey(bx, by, nb);
        if (visited.has(sk)) continue;
        visited.add(sk);
        q.push({
          px: bx, py: by, boxes: nb,
          path: cur.path + ch,
          moves: cur.moves.concat([{ ch, from: bk, to: tk, playerFrom: fk }])
        });
      }
    }
  }
  return { ok: false, ms: Date.now() - T0, exp };
}

const bfs = solveBFS(60000);
if (bfs.ok) {
  console.log(`BFS optimal pushes=${bfs.pushes} in ${bfs.ms}ms exp=${bfs.exp}`);
  console.log('path:', bfs.path);
  const rep2 = replayMoves(bfs.moves);
  console.log('BFS verify:', rep2.ok ? 'VALID ✓' : 'INVALID', rep2);
} else {
  console.log('BFS not finished', bfs);
}
