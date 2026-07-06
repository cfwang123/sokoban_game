// 批量求解器 - 为 levels.js 中没有答案的关卡自动求解
const fs = require('fs');
const path = require('path');

// 读取 levels.js 并提取数据
const levelsCode = fs.readFileSync(path.join(__dirname, '..', 'js', 'levels.js'), 'utf8');

// 用 Function 构造函数替代 eval，使 const 变量可访问
const getLevels = new Function(levelsCode + '\nreturn { LEVEL_NAMES, LEVEL_SOLUTIONS, LEVELS };');
const { LEVEL_NAMES, LEVEL_SOLUTIONS, LEVELS } = getLevels();

// 找到所有空解答的索引
const emptyIndices = [];
for (let i = 0; i < LEVEL_SOLUTIONS.length; i++) {
  if (LEVEL_SOLUTIONS[i] === '') emptyIndices.push(i);
}

console.log('总关卡数:', LEVELS.length);
console.log('空解答关卡数:', emptyIndices.length);
console.log('空解答索引:', emptyIndices.join(', '));
console.log('');

// ========== 求解器 ==========

function buildSolver(levelRows) {
  const W = new Set(), G = new Set();
  let P = null;

  for (let y = 0; y < levelRows.length; y++)
    for (let x = 0; x < levelRows[y].length; x++) {
      const c = levelRows[y][x], k = x+','+y;
      if (c === '#') W.add(k);
      else if (c === '.') G.add(k);
      else if (c === '$') {}
      else if (c === '*') { G.add(k); }
      else if (c === '@') P = {x,y};
      else if (c === '+') { P = {x,y}; G.add(k); }
    }

  // 预计算目标距离 & 邻居
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

  // 死格预计算
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

  function stateKey(px, py, boxes) {
    const arr = Array.from(boxes);
    arr.sort();
    return px+','+py+'|'+arr.join(';');
  }

  class MinHeap {
    constructor() { this.heap = []; }
    push(node) {
      this.heap.push(node);
      let i = this.heap.length - 1;
      while (i > 0) {
        const p = (i-1)>>1;
        if (this.heap[p].f <= this.heap[i].f) break;
        [this.heap[p], this.heap[i]] = [this.heap[i], this.heap[p]];
        i = p;
      }
    }
    pop() {
      if (this.heap.length === 1) return this.heap.pop();
      const top = this.heap[0];
      this.heap[0] = this.heap.pop();
      let i = 0;
      const n = this.heap.length;
      while (true) {
        let smallest = i;
        const l = i*2+1, r = i*2+2;
        if (l < n && this.heap[l].f < this.heap[smallest].f) smallest = l;
        if (r < n && this.heap[r].f < this.heap[smallest].f) smallest = r;
        if (smallest === i) break;
        [this.heap[i], this.heap[smallest]] = [this.heap[smallest], this.heap[i]];
        i = smallest;
      }
      return top;
    }
    get size() { return this.heap.length; }
  }

  const dirs = [[0,-1,'u'],[0,1,'d'],[-1,0,'l'],[1,0,'r']];
  const W_ASTAR = 2;

  return function solve(timeLimit) {
    // 解析初始状态
    const B = new Set();
    let P2 = null;
    for (let y = 0; y < levelRows.length; y++)
      for (let x = 0; x < levelRows[y].length; x++) {
        const c = levelRows[y][x], k = x+','+y;
        if (c === '$' || c === '*') B.add(k);
        if (c === '@' || c === '+') P2 = {x,y};
      }

    let startH = 0;
    for (const b of B) startH += goalDist[b];

    const startBoxes = new Set(B);
    const pq = new MinHeap();
    pq.push({px:P2.x, py:P2.y, boxes:startBoxes, path:[], f: W_ASTAR * startH, g: 0, h: startH});
    const visited = new Set([stateKey(P2.x, P2.y, startBoxes)]);
    const T0 = Date.now();
    let nodes = 0;

    while (pq.size > 0) {
      if (Date.now() - T0 > timeLimit) return null;

      const cur = pq.pop();
      nodes++;

      let won = true;
      for (const b of cur.boxes) { if (!G.has(b)) { won = false; break; } }
      if (won) return { path: cur.path.join(''), nodes };

      const r = reachable(cur.px, cur.py, cur.boxes);

      for (const bk of cur.boxes) {
        const [bx,by] = bk.split(',').map(Number);
        for (const [dx,dy,dn] of dirs) {
          const tk = (bx+dx)+','+(by+dy);
          const fk = (bx-dx)+','+(by-dy);
          if (W.has(tk) || cur.boxes.has(tk)) continue;
          if (!r.has(fk)) continue;
          if (deadCells.has(tk)) continue;

          const nb = new Set(cur.boxes);
          nb.delete(bk);
          nb.add(tk);

          if (check2x2(bx+dx, by+dy, nb)) continue;

          const npx = fk.split(',')[0]-0, npy = fk.split(',')[1]-0;
          const nk = stateKey(npx, npy, nb);
          if (visited.has(nk)) continue;
          visited.add(nk);

          const nh = cur.h - goalDist[bk] + goalDist[tk];

          pq.push({
            px: npx, py: npy, boxes: nb,
            path: cur.path.concat([dn]),
            f: cur.g + 1 + W_ASTAR * nh,
            g: cur.g + 1,
            h: nh
          });
        }
      }
    }

    return null;
  };
}

// ========== 批量求解 ==========

const TIME_LIMIT = 50000; // 每关5秒
const results = { solved: [], failed: [] };

for (let idx = 0; idx < emptyIndices.length; idx++) {
  const levelIdx = emptyIndices[idx];
  const name = LEVEL_NAMES[levelIdx];
  const levelRows = LEVELS[levelIdx];
  
  console.log(`[${idx+1}/${emptyIndices.length}] 求解: ${name} (索引 ${levelIdx})...`);
  
  const solve = buildSolver(levelRows);
  const result = solve(TIME_LIMIT);
  
  if (result) {
    console.log(`  ✓ 找到解! 步数: ${result.path.length}, 节点: ${result.nodes}`);
    console.log(`  路径: ${result.path}`);
    results.solved.push({ index: levelIdx, name, path: result.path });
  } else {
    console.log(`  ✗ 未找到解 (超时5秒)`);
    results.failed.push({ index: levelIdx, name });
  }
}

// ========== 输出结果 ==========

console.log('\n========================================');
console.log('求解完成!');
console.log('成功:', results.solved.length, '关');
console.log('失败:', results.failed.length, '关');
console.log('');

if (results.failed.length > 0) {
  console.log('失败的关卡:');
  for (const f of results.failed) {
    console.log(`  ${f.name} (索引 ${f.index})`);
  }
  console.log('');
}

console.log('找到的解答:');
for (const s of results.solved) {
  console.log(`  ${s.name}: "${s.path}"`);
}

// 生成更新后的 LEVEL_SOLUTIONS 代码片段
console.log('\n========================================');
console.log('更新 LEVEL_SOLUTIONS 的代码片段:');
console.log('');

const newSolutions = [...LEVEL_SOLUTIONS];
for (const s of results.solved) {
  newSolutions[s.index] = s.path;
}

// 输出从第一个空解答开始的连续代码块
let firstEmpty = emptyIndices[0];
let lastEmpty = emptyIndices[emptyIndices.length - 1];
console.log(`// 替换 LEVEL_SOLUTIONS 中索引 ${firstEmpty}~${lastEmpty} 的条目`);
console.log('const LEVEL_SOLUTIONS = [');
for (let i = 0; i < newSolutions.length; i++) {
  const comma = i < newSolutions.length - 1 ? ',' : '';
  console.log(`  "${newSolutions[i]}"${comma}`);
}
console.log('];');
