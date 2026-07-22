const level = require('../levels.json').find(l => l.id === 75);
const levelRows = level.puzzle;
const H = levelRows.length, WW = Math.max(...levelRows.map(r => r.length));
const rows = levelRows.map(r => r.padEnd(WW, '#'));
const flat = (x, y) => y * WW + x;
const cellX = [], cellY = [];
const wall = new Uint8Array(WW * H);
const xyToId = new Int16Array(WW * H).fill(-1);
let sx, sy;
const boxes = [], goals = [];
for (let y = 0; y < H; y++)
  for (let x = 0; x < WW; x++) {
    const c = rows[y][x];
    if (c === '#') { wall[flat(x, y)] = 1; continue; }
    const id = cellX.length;
    cellX.push(x); cellY.push(y); xyToId[flat(x, y)] = id;
    if ('.+*'.includes(c)) goals.push(id);
    if ('$*'.includes(c)) boxes.push(id);
    if ('@+'.includes(c)) { sx = x; sy = y; }
  }
const N = cellX.length;
const BITS = Array.from({ length: N }, (_, i) => 1n << BigInt(i));
let mask = 0n;
boxes.forEach(b => { mask |= BITS[b]; });
const DX = [0, 0, -1, 1], DY = [-1, 1, 0, 0];
const pushTo = new Int16Array(N * 4).fill(-1);
const pushFrom = new Int16Array(N * 4).fill(-1);
const neigh = Array.from({ length: N }, () => []);
for (let i = 0; i < N; i++) {
  const x = cellX[i], y = cellY[i];
  for (let d = 0; d < 4; d++) {
    const nx = x + DX[d], ny = y + DY[d];
    if (nx < 0 || ny < 0 || nx >= WW || ny >= H || wall[flat(nx, ny)]) continue;
    const nid = xyToId[flat(nx, ny)];
    if (nid < 0) continue;
    neigh[i].push(nid);
    const fx = x - DX[d], fy = y - DY[d];
    if (fx < 0 || fy < 0 || fx >= WW || fy >= H || wall[flat(fx, fy)]) continue;
    const fid = xyToId[flat(fx, fy)];
    if (fid < 0) continue;
    pushTo[i * 4 + d] = nid;
    pushFrom[i * 4 + d] = fid;
  }
}
const isGoal = new Uint8Array(N);
goals.forEach(g => { isGoal[g] = 1; });

// reverse dead
const dead = new Uint8Array(N);
const goalDist = new Int16Array(N).fill(32000);
{
  const q = [...goals];
  goals.forEach(g => { goalDist[g] = 0; });
  const alive = new Uint8Array(N);
  goals.forEach(g => { alive[g] = 1; });
  for (let qi = 0; qi < q.length; qi++) {
    const t = q[qi], x = cellX[t], y = cellY[t], bd = goalDist[t];
    for (let d = 0; d < 4; d++) {
      const Fx = x - DX[d], Fy = y - DY[d];
      const Px = x - 2 * DX[d], Py = y - 2 * DY[d];
      if (Fx < 0 || Fy < 0 || Fx >= WW || Fy >= H || wall[flat(Fx, Fy)]) continue;
      if (Px < 0 || Py < 0 || Px >= WW || Py >= H || wall[flat(Px, Py)]) continue;
      const fid = xyToId[flat(Fx, Fy)];
      if (fid < 0) continue;
      if (goalDist[fid] > bd + 1) { goalDist[fid] = bd + 1; alive[fid] = 1; q.push(fid); }
    }
  }
  for (let i = 0; i < N; i++) {
    if (!isGoal[i] && !alive[i]) dead[i] = 1;
  }
}

const reach = new Set();
const qq = [xyToId[flat(sx, sy)]];
reach.add(qq[0]);
for (let i = 0; i < qq.length; i++) {
  for (const n of neigh[qq[i]]) {
    if (!reach.has(n) && (mask & BITS[n]) === 0n) { reach.add(n); qq.push(n); }
  }
}
console.log('reach size', reach.size, [...reach].map(i => cellX[i] + ',' + cellY[i]).join(' '));

for (const b of boxes) {
  for (let d = 0; d < 4; d++) {
    const to = pushTo[b * 4 + d], from = pushFrom[b * 4 + d];
    if (to < 0 || (mask & BITS[to]) !== 0n || !reach.has(from)) continue;
    console.log('LEGAL', 'box', cellX[b] + ',' + cellY[b], 'd', d, 'to', cellX[to] + ',' + cellY[to], 'deadTo', !!dead[to]);
    if (dead[to]) continue;
    const nm = mask ^ BITS[b] ^ BITS[to];
    // freeze
    const freezeMark = new Uint8Array(N);
    const boxIds = [];
    for (let i = 0; i < N; i++) if ((nm & BITS[i]) !== 0n) boxIds.push(i);
    let changed = true;
    while (changed) {
      changed = false;
      for (const i of boxIds) {
        if (freezeMark[i]) continue;
        const x = cellX[i], y = cellY[i];
        const hard = (dx, dy) => {
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= WW || ny >= H || wall[flat(nx, ny)]) return true;
          const id = xyToId[flat(nx, ny)];
          return id >= 0 && (nm & BITS[id]) !== 0n && freezeMark[id] === 1;
        };
        if ((hard(-1, 0) && hard(1, 0)) || (hard(0, -1) && hard(0, 1))) {
          freezeMark[i] = 1; changed = true;
        }
      }
    }
    const bad = boxIds.filter(i => freezeMark[i] && !isGoal[i]);
    console.log('  freeze off-goal', bad.map(i => cellX[i] + ',' + cellY[i]));

    // 2x2
    const x = cellX[to], y = cellY[to];
    let d22 = false;
    for (let ox = -1; ox <= 0; ox++) for (let oy = -1; oy <= 0; oy++) {
      let allBox = true, anyGoal = false;
      outer:
      for (let dx = 0; dx <= 1; dx++) for (let dy = 0; dy <= 1; dy++) {
        const cx = x + ox + dx, cy = y + oy + dy;
        if (cx < 0 || cy < 0 || cx >= WW || cy >= H || wall[flat(cx, cy)]) { allBox = false; break outer; }
        const id = xyToId[flat(cx, cy)];
        if (id < 0 || (nm & BITS[id]) === 0n) { allBox = false; break outer; }
        if (isGoal[id]) anyGoal = true;
      }
      if (allBox && !anyGoal) d22 = true;
    }
    console.log('  2x2', d22);
  }
}

// Why is reach only 4? Print board with reach
console.log('\nBoard reach map:');
for (let y = 0; y < H; y++) {
  let line = '';
  for (let x = 0; x < WW; x++) {
    if (wall[flat(x, y)]) { line += '#'; continue; }
    const id = xyToId[flat(x, y)];
    if ((mask & BITS[id]) !== 0n) line += '$';
    else if (reach.has(id)) line += '+';
    else line += '.';
  }
  console.log(line);
}
