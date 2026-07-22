/**
 * Sokoban 求解器 v6 — 冲 65 L (12箱) < 5s
 *
 * 策略（auto 依次尝试，共享时限）：
 *  A. Greedy-DFS：按 Δh 排序 + 同箱惯性，深度优先（常最快出解）
 *  B. Greedy-BF：best-first 堆
 *  C. Reverse greedy-DFS：终局 pull
 *
 * 剪枝：反向死格、2x2、freeze、PI-corral、transposition
 */
const fs = require('fs');
const path = require('path');

function buildSolver(levelRows) {
  const H = levelRows.length;
  const WW = Math.max(...levelRows.map(r => r.length));
  const rows = levelRows.map(r => r.padEnd(WW, '#'));
  const flat = (x, y) => y * WW + x;

  const cellX = [], cellY = [];
  const wall = new Uint8Array(WW * H);
  const xyToId = new Int16Array(WW * H).fill(-1);
  let sx = 0, sy = 0;
  const startBoxList = [], goalList = [];

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < WW; x++) {
      const c = rows[y][x];
      if (c === '#') { wall[flat(x, y)] = 1; continue; }
      const id = cellX.length;
      cellX.push(x); cellY.push(y);
      xyToId[flat(x, y)] = id;
      if (c === '.' || c === '*' || c === '+') goalList.push(id);
      if (c === '$' || c === '*') startBoxList.push(id);
      if (c === '@' || c === '+') { sx = x; sy = y; }
    }
  }

  const N = cellX.length;
  const NB = startBoxList.length;
  const NG = goalList.length;
  const isGoal = new Uint8Array(N);
  for (const g of goalList) isGoal[g] = 1;
  const startPlayer = xyToId[flat(sx, sy)];

  const DX = [0, 0, -1, 1], DY = [-1, 1, 0, 0];
  const DCH = ['u', 'd', 'l', 'r'];
  const OPPCH = ['d', 'u', 'r', 'l'];

  const neigh = new Int16Array(N * 4).fill(-1);
  const pushTo = new Int16Array(N * 4).fill(-1);
  const pushFrom = new Int16Array(N * 4).fill(-1);

  for (let i = 0; i < N; i++) {
    const x = cellX[i], y = cellY[i];
    for (let d = 0; d < 4; d++) {
      const nx = x + DX[d], ny = y + DY[d];
      if (nx < 0 || ny < 0 || nx >= WW || ny >= H || wall[flat(nx, ny)]) continue;
      const nid = xyToId[flat(nx, ny)];
      if (nid < 0) continue;
      neigh[i * 4 + d] = nid;
      const fx = x - DX[d], fy = y - DY[d];
      if (fx < 0 || fy < 0 || fx >= WW || fy >= H || wall[flat(fx, fy)]) continue;
      const fid = xyToId[flat(fx, fy)];
      if (fid < 0) continue;
      pushTo[i * 4 + d] = nid;
      pushFrom[i * 4 + d] = fid;
    }
  }

  const exterior = new Uint8Array(N);
  {
    const q = [];
    for (let i = 0; i < N; i++) {
      const x = cellX[i], y = cellY[i];
      if (x === 0 || y === 0 || x === WW - 1 || y === H - 1) {
        exterior[i] = 1; q.push(i);
      }
    }
    for (let qi = 0; qi < q.length; qi++) {
      for (let d = 0; d < 4; d++) {
        const n = neigh[q[qi] * 4 + d];
        if (n >= 0 && !exterior[n]) { exterior[n] = 1; q.push(n); }
      }
    }
  }

  const dead = new Uint8Array(N);
  const goalDist = new Int16Array(N).fill(32000);
  const startDist = new Int16Array(N).fill(32000);
  {
    const q = new Int16Array(N * 2);
    const revExpand = (sources, distArr) => {
      distArr.fill(32000);
      let qh = 0, qt = 0;
      for (const s of sources) { distArr[s] = 0; q[qt++] = s; }
      while (qh < qt) {
        const t = q[qh++];
        const x = cellX[t], y = cellY[t], bd = distArr[t];
        for (let d = 0; d < 4; d++) {
          const Fx = x - DX[d], Fy = y - DY[d];
          const Px = x - 2 * DX[d], Py = y - 2 * DY[d];
          if (Fx < 0 || Fy < 0 || Fx >= WW || Fy >= H || wall[flat(Fx, Fy)]) continue;
          if (Px < 0 || Py < 0 || Px >= WW || Py >= H || wall[flat(Px, Py)]) continue;
          const fid = xyToId[flat(Fx, Fy)];
          if (fid < 0) continue;
          if (distArr[fid] > bd + 1) { distArr[fid] = bd + 1; q[qt++] = fid; }
        }
      }
    };
    revExpand(goalList, goalDist);
    // startDist[c] = push-dist from start-box-cells TO c
    // = reverse-BFS sources=starts gives dist from c TO start; we need opposite.
    // Forward push BFS from starts:
    {
      startDist.fill(32000);
      let qh = 0, qt = 0;
      for (const s of startBoxList) { startDist[s] = 0; q[qt++] = s; }
      while (qh < qt) {
        const f = q[qh++];
        const x = cellX[f], y = cellY[f], bd = startDist[f];
        for (let d = 0; d < 4; d++) {
          // forward push F→T=F+d needs F-d free (static ignore boxes)
          const Tx = x + DX[d], Ty = y + DY[d];
          const Px = x - DX[d], Py = y - DY[d];
          if (Tx < 0 || Ty < 0 || Tx >= WW || Ty >= H || wall[flat(Tx, Ty)]) continue;
          if (Px < 0 || Py < 0 || Px >= WW || Py >= H || wall[flat(Px, Py)]) continue;
          const tid = xyToId[flat(Tx, Ty)];
          if (tid < 0) continue;
          if (startDist[tid] > bd + 1) { startDist[tid] = bd + 1; q[qt++] = tid; }
        }
      }
    }

    const alive = new Uint8Array(N);
    for (let i = 0; i < N; i++) if (goalDist[i] < 32000) alive[i] = 1;
    for (let i = 0; i < N; i++) {
      if (isGoal[i]) continue;
      if (!alive[i]) { dead[i] = 1; continue; }
      const x = cellX[i], y = cellY[i];
      const u = y === 0 || wall[flat(x, y - 1)];
      const dn = y === H - 1 || wall[flat(x, y + 1)];
      const l = x === 0 || wall[flat(x - 1, y)];
      const r = x === WW - 1 || wall[flat(x + 1, y)];
      if ((u && l) || (u && r) || (dn && l) || (dn && r)) dead[i] = 1;
      else if (u && dn && (l || r)) dead[i] = 1;
      else if (l && r && (u || dn)) dead[i] = 1;
    }
  }

  const degree = new Uint8Array(N);
  for (let i = 0; i < N; i++) {
    let d = 0;
    for (let k = 0; k < 4; k++) if (neigh[i * 4 + k] >= 0) d++;
    degree[i] = d;
  }

  const BITS = new Array(N);
  for (let i = 0; i < N; i++) BITS[i] = 1n << BigInt(i);
  let startMask = 0n, goalMask = 0n;
  for (const b of startBoxList) startMask |= BITS[b];
  for (const g of goalList) goalMask |= BITS[g];

  // ---- reach ----
  const visitGen = new Uint32Array(N);
  const bfsQ = new Int16Array(N);
  let gen = 1;
  function computeReach(player, mask) {
    gen++;
    if (gen >= 0xffffff00) { visitGen.fill(0); gen = 1; }
    let qh = 0, qt = 0, minR = player;
    bfsQ[qt++] = player;
    visitGen[player] = gen;
    while (qh < qt) {
      const c = bfsQ[qh++];
      if (c < minR) minR = c;
      for (let d = 0; d < 4; d++) {
        const n = neigh[c * 4 + d];
        if (n < 0 || visitGen[n] === gen) continue;
        if ((mask & BITS[n]) !== 0n) continue;
        visitGen[n] = gen;
        bfsQ[qt++] = n;
      }
    }
    return minR;
  }
  function canReach(c) { return visitGen[c] === gen; }

  function is2x2(mask, movedTo) {
    const x = cellX[movedTo], y = cellY[movedTo];
    for (let ox = -1; ox <= 0; ox++) for (let oy = -1; oy <= 0; oy++) {
      let all = true, anyG = false;
      outer:
      for (let dx = 0; dx <= 1; dx++) for (let dy = 0; dy <= 1; dy++) {
        const cx = x + ox + dx, cy = y + oy + dy;
        if (cx < 0 || cy < 0 || cx >= WW || cy >= H || wall[flat(cx, cy)]) { all = false; break outer; }
        const id = xyToId[flat(cx, cy)];
        if (id < 0 || (mask & BITS[id]) === 0n) { all = false; break outer; }
        if (isGoal[id]) anyG = true;
      }
      if (all && !anyG) return true;
    }
    return false;
  }

  const freezeMark = new Uint8Array(N);
  function isFreezeDead(mask) {
    freezeMark.fill(0);
    let changed = true, guard = 0;
    while (changed && guard++ < NB + 2) {
      changed = false;
      for (let i = 0; i < N; i++) {
        if ((mask & BITS[i]) === 0n || freezeMark[i]) continue;
        const x = cellX[i], y = cellY[i];
        const solid = (dx, dy) => {
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= WW || ny >= H || wall[flat(nx, ny)]) return true;
          const id = xyToId[flat(nx, ny)];
          return id >= 0 && (mask & BITS[id]) !== 0n && freezeMark[id] === 1;
        };
        // 两轴都锁才冻结
        if (solid(-1, 0) && solid(1, 0) && solid(0, -1) && solid(0, 1)) {
          freezeMark[i] = 1; changed = true;
        }
      }
    }
    for (let i = 0; i < N; i++) {
      if ((mask & BITS[i]) !== 0n && freezeMark[i] && !isGoal[i]) return true;
    }
    return false;
  }

  function hFwd(mask) {
    let h = 0;
    for (let i = 0; i < N; i++) {
      if ((mask & BITS[i]) !== 0n) {
        const d = goalDist[i];
        if (d >= 32000) return 999999;
        h += d;
      }
    }
    return h;
  }
  function hRev(mask) {
    let h = 0;
    for (let i = 0; i < N; i++) {
      if ((mask & BITS[i]) !== 0n) {
        const d = startDist[i];
        if (d >= 32000) return 999999;
        h += d;
      }
    }
    return h;
  }

  function isWin(mask) {
    for (let i = 0; i < N; i++) {
      if ((mask & BITS[i]) !== 0n && !isGoal[i]) return false;
    }
    return true;
  }

  // Generate forward push children: [{mask, player, ch, h, box, pushes}]
  function genPushes(player, mask, lastBox) {
    computeReach(player, mask);
    const moves = [];
    for (let b = 0; b < N; b++) {
      if ((mask & BITS[b]) === 0n) continue;
      for (let d = 0; d < 4; d++) {
        const to = pushTo[b * 4 + d];
        if (to < 0) continue;
        if ((mask & BITS[to]) !== 0n) continue;
        const from = pushFrom[b * 4 + d];
        if (!canReach(from)) continue;
        if (dead[to]) continue;

        let nm = mask ^ BITS[b] ^ BITS[to];
        let fTo = to, fPl = b, pc = 1, ch = DCH[d];
        while (degree[fTo] === 2 && !isGoal[fTo]) {
          const nx = pushTo[fTo * 4 + d];
          if (nx < 0 || (nm & BITS[nx]) !== 0n || dead[nx]) break;
          nm ^= BITS[fTo] ^ BITS[nx];
          fPl = fTo; fTo = nx; pc++; ch += DCH[d];
          if (pc > 12) break;
        }
        if (is2x2(nm, fTo)) continue;
        if (isFreezeDead(nm)) continue;
        const nh = hFwd(nm);
        if (nh >= 999999) continue;
        // score: lower better. bonus for reducing h, same box, parking on goal
        let score = nh;
        if (b === lastBox) score -= 0.5;
        if (isGoal[fTo] && !isGoal[b]) score -= 0.25;
        if (isGoal[b] && !isGoal[fTo]) score += 1.5; // avoid unparking
        moves.push({ mask: nm, player: fPl, ch, h: nh, box: fTo, pushes: pc, score, fromBox: b });
      }
    }
    // PI-corral prune: if interior corral with I-only fence, keep fence moves only
    const filtered = piFilter(mask, moves);
    const list = filtered || moves;
    list.sort((a, b) => a.score - b.score);
    return list;
  }

  const corralGen = new Uint32Array(N);
  let cgen = 1;
  function piFilter(mask, moves) {
    cgen++;
    if (cgen >= 0xffffff00) { corralGen.fill(0); cgen = 1; }
    let has = false;
    for (let i = 0; i < N; i++) {
      if ((mask & BITS[i]) !== 0n || visitGen[i] === gen || exterior[i]) continue;
      corralGen[i] = cgen; has = true;
    }
    if (!has) return null;

    const seen = new Uint8Array(N);
    for (let seed = 0; seed < N; seed++) {
      if (corralGen[seed] !== cgen || seen[seed]) continue;
      let qh = 0, qt = 0;
      bfsQ[qt++] = seed; seen[seed] = 1;
      let fence = 0n, fc = 0;
      while (qh < qt) {
        const c = bfsQ[qh++];
        for (let d = 0; d < 4; d++) {
          const n = neigh[c * 4 + d];
          if (n < 0) continue;
          if ((mask & BITS[n]) !== 0n) {
            if ((fence & BITS[n]) === 0n) { fence |= BITS[n]; fc++; }
          } else if (corralGen[n] === cgen && !seen[n]) {
            seen[n] = 1; bfsQ[qt++] = n;
          }
        }
      }
      if (fc === 0) continue;
      let ok = true, any = false;
      for (let b = 0; b < N && ok; b++) {
        if ((fence & BITS[b]) === 0n) continue;
        for (let d = 0; d < 4; d++) {
          const to = pushTo[b * 4 + d];
          if (to < 0 || (mask & BITS[to]) !== 0n) continue;
          const from = pushFrom[b * 4 + d];
          if (visitGen[from] !== gen || dead[to]) continue;
          any = true;
          if (corralGen[to] !== cgen) { ok = false; break; }
        }
      }
      if (!ok || !any) continue;
      const out = moves.filter(m => (fence & BITS[m.fromBox]) !== 0n);
      if (out.length) return out;
    }
    return null;
  }

  // ========== Greedy DFS ==========
  function solveDFS(tl) {
    const T0 = Date.now();
    const visited = new Map(); // key -> best g
    let nodes = 0, expansions = 0;
    let solution = null;

    function key(mask, minR) { return mask.toString(36) + '|' + minR; }

    function dfs(mask, player, g, path, lastBox) {
      if (solution) return true;
      if ((expansions & 1023) === 0 && Date.now() - T0 > tl) return false;
      expansions++;

      if (isWin(mask)) {
        solution = { path, g, nodes, expansions, ms: Date.now() - T0 };
        return true;
      }

      const moves = genPushes(player, mask, lastBox);
      for (const m of moves) {
        nodes++;
        const minR = computeReach(m.player, m.mask);
        const k = key(m.mask, minR);
        const prev = visited.get(k);
        const ng = g + m.pushes;
        if (prev !== undefined && prev <= ng) continue;
        visited.set(k, ng);
        if (dfs(m.mask, m.player, ng, path + m.ch, m.fromBox)) return true;
      }
      return false;
    }

    const min0 = computeReach(startPlayer, startMask);
    visited.set(key(startMask, min0), 0);
    dfs(startMask, startPlayer, 0, '', -1);

    if (solution) {
      return {
        ok: true, path: solution.path, pushes: solution.g,
        nodes, expansions, ms: Date.now() - T0, dir: 'dfs', visited: visited.size
      };
    }
    return { ok: false, nodes, expansions, ms: Date.now() - T0, dir: 'dfs', visited: visited.size };
  }

  // ========== Greedy Best-First ==========
  class MinHeap {
    constructor() { this.a = []; }
    push(n) {
      const a = this.a; a.push(n);
      let i = a.length - 1;
      while (i > 0) {
        const p = (i - 1) >> 1;
        if (a[p].f <= a[i].f) break;
        const t = a[p]; a[p] = a[i]; a[i] = t; i = p;
      }
    }
    pop() {
      const a = this.a;
      if (a.length === 1) return a.pop();
      const top = a[0]; a[0] = a.pop();
      let i = 0, n = a.length;
      for (;;) {
        let s = i, l = 2 * i + 1, r = 2 * i + 2;
        if (l < n && a[l].f < a[s].f) s = l;
        if (r < n && a[r].f < a[s].f) s = r;
        if (s === i) break;
        const t = a[i]; a[i] = a[s]; a[s] = t; i = s;
      }
      return top;
    }
    get size() { return this.a.length; }
  }

  function solveBF(tl) {
    const T0 = Date.now();
    const h0 = hFwd(startMask);
    if (h0 >= 999999) return { ok: false, nodes: 0, ms: 0, dir: 'bf' };
    const pq = new MinHeap();
    const visited = new Map();
    const min0 = computeReach(startPlayer, startMask);
    pq.push({ mask: startMask, player: startPlayer, g: 0, f: h0, path: '', lastBox: -1 });
    visited.set(startMask.toString(36) + '|' + min0, 0);
    let nodes = 0, expansions = 0;

    while (pq.size > 0) {
      if ((expansions & 511) === 0 && Date.now() - T0 > tl) {
        return { ok: false, nodes, expansions, ms: Date.now() - T0, dir: 'bf', visited: visited.size };
      }
      const cur = pq.pop();
      expansions++;
      if (isWin(cur.mask)) {
        return {
          ok: true, path: cur.path, pushes: cur.g, nodes, expansions,
          ms: Date.now() - T0, dir: 'bf', visited: visited.size
        };
      }
      const moves = genPushes(cur.player, cur.mask, cur.lastBox);
      for (const m of moves) {
        nodes++;
        const minR = computeReach(m.player, m.mask);
        const k = m.mask.toString(36) + '|' + minR;
        const ng = cur.g + m.pushes;
        const prev = visited.get(k);
        if (prev !== undefined && prev <= ng) continue;
        visited.set(k, ng);
        pq.push({
          mask: m.mask, player: m.player, g: ng, f: m.h,
          path: cur.path + m.ch, lastBox: m.fromBox
        });
      }
    }
    return { ok: false, nodes, expansions, ms: Date.now() - T0, dir: 'bf', visited: visited.size };
  }

  // ========== Reverse DFS ==========
  function genPulls(player, mask, lastBox) {
    computeReach(player, mask);
    const moves = [];
    for (let b = 0; b < N; b++) {
      if ((mask & BITS[b]) === 0n) continue;
      for (let d = 0; d < 4; d++) {
        const x = cellX[b], y = cellY[b];
        const px = x + DX[d], py = y + DY[d];
        const p2x = x + 2 * DX[d], p2y = y + 2 * DY[d];
        if (px < 0 || py < 0 || px >= WW || py >= H || wall[flat(px, py)]) continue;
        if (p2x < 0 || p2y < 0 || p2x >= WW || p2y >= H || wall[flat(p2x, p2y)]) continue;
        const pid = xyToId[flat(px, py)], p2id = xyToId[flat(p2x, p2y)];
        if (pid < 0 || p2id < 0) continue;
        if ((mask & BITS[pid]) !== 0n || (mask & BITS[p2id]) !== 0n) continue;
        if (!canReach(pid)) continue;
        if (startDist[pid] >= 32000) continue;

        let nm = mask ^ BITS[b] ^ BITS[pid];
        let fBox = pid, fPl = p2id, pc = 1;
        const dirs = [d];
        while (degree[fBox] === 2) {
          const nx = cellX[fBox] + DX[d], ny = cellY[fBox] + DY[d];
          const n2x = cellX[fBox] + 2 * DX[d], n2y = cellY[fBox] + 2 * DY[d];
          if (nx < 0 || ny < 0 || nx >= WW || ny >= H || wall[flat(nx, ny)]) break;
          if (n2x < 0 || n2y < 0 || n2x >= WW || n2y >= H || wall[flat(n2x, n2y)]) break;
          const nid = xyToId[flat(nx, ny)], n2id = xyToId[flat(n2x, n2y)];
          if (nid < 0 || n2id < 0) break;
          if ((nm & BITS[nid]) !== 0n || (nm & BITS[n2id]) !== 0n) break;
          if (startDist[nid] >= 32000) break;
          nm ^= BITS[fBox] ^ BITS[nid];
          fPl = n2id; fBox = nid; pc++; dirs.push(d);
          if (pc > 12) break;
        }
        if (is2x2(nm, fBox)) continue;
        const nh = hRev(nm);
        if (nh >= 999999) continue;
        let score = nh;
        if (b === lastBox) score -= 0.5;
        moves.push({ mask: nm, player: fPl, h: nh, score, dirs, pushes: pc, fromBox: b });
      }
    }
    moves.sort((a, b) => a.score - b.score);
    return moves;
  }

  function solveRevDFS(tl) {
    const T0 = Date.now();
    const h0 = hRev(goalMask);
    if (h0 >= 999999) return { ok: false, nodes: 0, ms: 0, dir: 'rev', reason: 'h0' };

    // seed players: non-goal free cells components
    const seeds = [];
    {
      const seen = new Uint8Array(N);
      for (let i = 0; i < N; i++) {
        if (isGoal[i] || seen[i]) continue;
        // skip pure exterior-only components that don't touch a goal-adjacent free cell
        let qh = 0, qt = 0, minR = i, touches = false;
        bfsQ[qt++] = i; seen[i] = 1;
        while (qh < qt) {
          const c = bfsQ[qh++];
          if (c < minR) minR = c;
          for (let d = 0; d < 4; d++) {
            const n = neigh[c * 4 + d];
            if (n < 0) continue;
            if (isGoal[n]) { touches = true; continue; }
            if (seen[n]) continue;
            seen[n] = 1; bfsQ[qt++] = n;
          }
        }
        if (touches || !exterior[minR]) seeds.push(minR);
      }
    }
    if (!seeds.length) {
      // fallback: any free cell next to a goal
      for (const g of goalList) {
        for (let d = 0; d < 4; d++) {
          const n = neigh[g * 4 + d];
          if (n >= 0 && !isGoal[n]) seeds.push(n);
        }
      }
    }
    if (!seeds.length) return { ok: false, nodes: 0, ms: 0, dir: 'rev', reason: 'no seed' };

    const visited = new Map();
    let nodes = 0, expansions = 0, solution = null;

    function dfs(mask, player, g, pulls, lastBox) {
      if (solution) return true;
      if ((expansions & 1023) === 0 && Date.now() - T0 > tl) return false;
      expansions++;

      if (mask === startMask) {
        // convert pulls to forward pushes
        let path = '';
        for (let i = pulls.length - 1; i >= 0; i--) path += OPPCH[pulls[i]];
        solution = { path, g };
        return true;
      }

      const moves = genPulls(player, mask, lastBox);
      for (const m of moves) {
        nodes++;
        const minR = computeReach(m.player, m.mask);
        const k = m.mask.toString(36) + '|' + minR;
        const ng = g + m.pushes;
        const prev = visited.get(k);
        if (prev !== undefined && prev <= ng) continue;
        visited.set(k, ng);
        if (dfs(m.mask, m.player, ng, pulls.concat(m.dirs), m.fromBox)) return true;
      }
      return false;
    }

    for (const pl of seeds) {
      const minR = computeReach(pl, goalMask);
      const k = goalMask.toString(36) + '|' + minR;
      if (visited.has(k)) continue;
      visited.set(k, 0);
      if (dfs(goalMask, pl, 0, [], -1)) break;
      if (Date.now() - T0 > tl) break;
    }

    if (solution) {
      return {
        ok: true, path: solution.path, pushes: solution.g,
        nodes, expansions, ms: Date.now() - T0, dir: 'rev', visited: visited.size
      };
    }
    return { ok: false, nodes, expansions, ms: Date.now() - T0, dir: 'rev', visited: visited.size };
  }

  function solve(tl, mode) {
    mode = mode || 'auto';
    const T0 = Date.now();

    if (mode === 'dfs') return solveDFS(tl);
    if (mode === 'bf' || mode === 'greedy' || mode === 'fwd') return solveBF(tl);
    if (mode === 'rev') return solveRevDFS(tl);

    // auto: DFS 40% → rev 30% → BF rest
    const parts = [
      ['dfs', 0.4],
      ['rev', 0.3],
      ['bf', 0.3]
    ];
    let last = null;
    let totalNodes = 0, totalExp = 0;
    for (const [m, frac] of parts) {
      const used = Date.now() - T0;
      if (used >= tl) break;
      const budget = Math.max(50, Math.floor(tl * frac));
      const remain = tl - used;
      const t = Math.min(budget, remain);
      let r;
      if (m === 'dfs') r = solveDFS(t);
      else if (m === 'rev') r = solveRevDFS(t);
      else r = solveBF(t);
      totalNodes += r.nodes || 0;
      totalExp += r.expansions || 0;
      last = r;
      if (r.ok) {
        r.ms = Date.now() - T0;
        r.nodes = totalNodes;
        r.expansions = totalExp;
        return r;
      }
    }
    return {
      ok: false,
      nodes: totalNodes,
      expansions: totalExp,
      ms: Date.now() - T0,
      dir: 'auto',
      last
    };
  }

  return { solve, solveDFS, solveBF, solveRevDFS, N, NB, hFwd };
}

function main() {
  const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'levels.json'), 'utf8'));
  const levelId = process.argv[2] !== undefined ? +process.argv[2] : 128;
  const timeLimit = process.argv[3] !== undefined ? +process.argv[3] : 5000;
  const mode = (process.argv[4] || 'auto').toLowerCase();
  const level = data.find(l => l.id === levelId) || data[levelId];
  if (!level) { console.error('Level not found'); process.exit(1); }

  console.log(`Level id=${level.id} name=${level.name} mode=${mode}`);
  level.puzzle.forEach(r => console.log('  ' + r));

  const { solve } = buildSolver(level.puzzle);
  console.log(`\nSolving (limit ${timeLimit}ms)...`);
  const r = solve(timeLimit, mode);
  if (r.ok) {
    console.log(`SOLVED in ${r.ms}ms  pushes=${r.pushes}  nodes=${r.nodes}  exp=${r.expansions}  dir=${r.dir}`);
    console.log(`path: ${r.path}`);
  } else {
    console.log(`FAILED in ${r.ms}ms  nodes=${r.nodes}  exp=${r.expansions}  dir=${r.dir}  visited=${r.visited || (r.last && r.last.visited)}`);
    if (r.last) console.log('  last:', r.last.dir, r.last.ms + 'ms', 'nodes', r.last.nodes);
  }
}

module.exports = { buildSolver };
if (require.main === module) main();
