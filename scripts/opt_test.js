// Sokoban 求解器 - IDA* with transposition table
// 关卡从 levels.json#L882-891 提取


/*
#######
#. . .#
# $$$ #
#.$@$.#
# $$$ #
#. . .#
#######
*/
const rawRows = [
  "#######",
  "#. . .#",
  "# $$$ #",
  "#.$@$.#",
  "# $$$ #",
  "#. . .#",
  "#######",
];

// 统一宽度，缺失格视为墙
const maxW = Math.max(...rawRows.map(r => r.length));
const levelRows = rawRows.map(r => r.padEnd(maxW, '#'));

const W = new Set(), G = new Set(), B = new Set();
let P = null;

for (let y = 0; y < levelRows.length; y++)
  for (let x = 0; x < levelRows[y].length; x++) {
    const c = levelRows[y][x], k = x+','+y;
    if (c === '#') W.add(k);
    else if (c === '.') G.add(k);
    else if (c === '$') B.add(k);
    else if (c === '*') { B.add(k); G.add(k); }
    else if (c === '@') P = {x,y};
    else if (c === '+') { P = {x,y}; G.add(k); }
  }

console.log('Boxes:', B.size, 'Goals:', G.size);

// ========== 预计算 ==========
const goalDist = {};
const allCells = [];
const neighbors = {};

for (let y = 0; y < levelRows.length; y++)
  for (let x = 0; x < levelRows[y].length; x++) {
    const k = x+','+y;
    if (W.has(k)) continue;
    allCells.push(k);
    let md = Infinity;
    for (const g of G) {
      const [gx,gy] = g.split(',').map(Number);
      md = Math.min(md, Math.abs(x-gx)+Math.abs(y-gy));
    }
    goalDist[k] = md;
    const ns = [];
    for (const [dx,dy] of [[0,-1],[0,1],[-1,0],[1,0]]) {
      const nk = (x+dx)+','+(y+dy);
      if (!W.has(nk)) ns.push(nk);
    }
    neighbors[k] = ns;
  }

// 死格
const deadCells = new Set();
for (const cell of allCells) {
  if (G.has(cell)) continue;
  const [x,y] = cell.split(',').map(Number);
  const u = W.has(x+','+(y-1)), d = W.has(x+','+(y+1));
  const l = W.has((x-1)+','+y), r = W.has((x+1)+','+y);
  if ((u&&l)||(u&&r)||(d&&l)||(d&&r)) { deadCells.add(cell); continue; }
  if ((u && d) && (l || r)) { deadCells.add(cell); continue; }
  if ((l && r) && (u || d)) { deadCells.add(cell); continue; }
}

// 预计算推方向
const pushDirs = {};
for (const cell of allCells) {
  const [x,y] = cell.split(',').map(Number);
  const dirs = [];
  for (const [dx,dy,dn] of [[0,-1,'u'],[0,1,'d'],[-1,0,'l'],[1,0,'r']]) {
    const tk = (x+dx)+','+(y+dy);
    const fk = (x-dx)+','+(y-dy);
    if (!W.has(tk) && !W.has(fk)) dirs.push([dx,dy,dn]);
  }
  pushDirs[cell] = dirs;
}

// ========== BFS 可达区域 ==========
function reachable(px, py, boxes) {
  const seen = new Set();
  const q = [px+','+py];
  seen.add(q[0]);
  for (let i = 0; i < q.length; i++) {
    for (const nk of neighbors[q[i]]) {
      if (!seen.has(nk) && !boxes.has(nk)) {
        seen.add(nk);
        q.push(nk);
      }
    }
  }
  return seen;
}

// ========== 2x2 死锁 ==========
function check2x2(bx, by, boxes) {
  for (const [dx,dy] of [[0,0],[-1,0],[0,-1],[-1,-1]]) {
    const c1 = (bx+dx)+','+(by+dy);
    const c2 = (bx+dx+1)+','+(by+dy);
    const c3 = (bx+dx)+','+(by+dy+1);
    const c4 = (bx+dx+1)+','+(by+dy+1);
    if (boxes.has(c1) && boxes.has(c2) && boxes.has(c3) && boxes.has(c4)) {
      if (!G.has(c1) && !G.has(c2) && !G.has(c3) && !G.has(c4)) return true;
    }
  }
  return false;
}

// ========== Freeze 死锁 ==========
function checkFreezeDeadlock(boxes) {
  const onGoal = [], offGoal = [];
  for (const b of boxes) {
    if (G.has(b)) onGoal.push(b);
    else offGoal.push(b);
  }
  if (onGoal.length === 0 || offGoal.length === 0) return false;
  const frozen = new Set();
  let changed = true;
  while (changed) {
    changed = false;
    for (const b of onGoal) {
      if (frozen.has(b)) continue;
      const [x,y] = b.split(',').map(Number);
      let blocked = 0;
      for (const [dx,dy] of [[0,-1],[0,1],[-1,0],[1,0]]) {
        const nk = (x+dx)+','+(y+dy);
        if (W.has(nk)) blocked++;
        else if (frozen.has(nk)) blocked++;
        else if (boxes.has(nk) && G.has(nk)) blocked++;
      }
      if (blocked === 4) { frozen.add(b); changed = true; }
    }
  }
  return frozen.size === onGoal.length;
}

// ========== 启发式：贪心匹配 ==========
const goalArr = Array.from(G);
function heuristic(boxes) {
  const boxArr = Array.from(boxes);
  const n = boxArr.length;
  const gn = goalArr.length;
  const used = new Set();
  let total = 0;
  for (let i = 0; i < n; i++) {
    const [bx, by] = boxArr[i].split(',').map(Number);
    let best = Infinity, bestJ = -1;
    for (let j = 0; j < gn; j++) {
      if (used.has(j)) continue;
      const [gx, gy] = goalArr[j].split(',').map(Number);
      const d = Math.abs(bx - gx) + Math.abs(by - gy);
      if (d < best) { best = d; bestJ = j; }
    }
    used.add(bestJ);
    total += best;
  }
  return total;
}

// ========== 状态键 ==========
function stateKey(px, py, boxes) {
  const arr = Array.from(boxes);
  arr.sort();
  return px+','+py+'|'+arr.join(';');
}

const dirs = [[0,-1,'u'],[0,1,'d'],[-1,0,'l'],[1,0,'r']];
const T0 = Date.now();
const TL = 50000;
let nodes = 0;
let solution = null;

// ========== IDA* ==========
function dfs(px, py, boxes, g, path, bound, visited) {
  if (solution) return -2; // 已找到解
  if (Date.now() - T0 > TL) return -2;

  const h = heuristic(boxes);
  const f = g + h;

  if (f > bound) return f;

  // 检查胜利
  let won = true;
  for (const b of boxes) { if (!G.has(b)) { won = false; break; } }
  if (won) {
    solution = { path: path.slice(), nodes };
    return -2;
  }

  const r = reachable(px, py, boxes);
  const moves = [];

  for (const bk of boxes) {
    const [bx, by] = bk.split(',').map(Number);
    for (const [dx, dy, dn] of pushDirs[bk] || dirs) {
      const tk = (bx+dx)+','+(by+dy);
      const fk = (bx-dx)+','+(by-dy);
      if (W.has(tk) || boxes.has(tk)) continue;
      if (!r.has(fk)) continue;
      if (deadCells.has(tk)) continue;

      const nb = new Set(boxes);
      nb.delete(bk);
      nb.add(tk);

      if (check2x2(bx+dx, by+dy, nb)) continue;
      if (checkFreezeDeadlock(nb)) continue;

      const npx = fk.split(',')[0]-0, npy = fk.split(',')[1]-0;
      const nk = stateKey(npx, npy, nb);
      if (visited.has(nk)) continue;

      const nh = heuristic(nb);
      moves.push({ px: npx, py: npy, boxes: nb, path: dn, key: nk, f: g + 1 + nh });
    }
  }

  // 按 f 排序
  moves.sort((a, b) => a.f - b.f);

  let nextBound = Infinity;
  for (const m of moves) {
    nodes++;
    visited.add(m.key);
    const t = dfs(m.px, m.py, m.boxes, g + 1, path.concat([m.path]), bound, visited);
    visited.delete(m.key);
    if (solution) return -2;
    if (t !== -2 && t < nextBound) nextBound = t;
  }

  return nextBound;
}

function solve() {
  const startBoxes = new Set(B);
  let bound = heuristic(startBoxes);
  const visited = new Set();

  while (!solution && Date.now() - T0 <= TL) {
    visited.clear();
    visited.add(stateKey(P.x, P.y, startBoxes));
    const t = dfs(P.x, P.y, startBoxes, 0, [], bound, visited);
    if (solution) break;
    if (t === Infinity) break;
    bound = t;
  }

  return solution;
}

console.log('开始求解...');
const r = solve();
if (r) {
  console.log('找到解! 步数:', r.path.length, '节点:', r.nodes);
  console.log('路径:', r.path.join(','));
} else {
  console.log('未找到解');
}
