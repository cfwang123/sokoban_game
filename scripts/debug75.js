const { buildSolver } = require('./solver_opt.js');
const level = require('../levels.json').find(l => l.id === 75);

// Monkey: reimplement minimal parse for debug
const levelRows = level.puzzle;
const H = levelRows.length;
const WW = Math.max(...levelRows.map(r => r.length));
const rows = levelRows.map(r => r.padEnd(WW, '#'));
console.log(rows.join('\n'));

const cellX = [], cellY = [];
const wall = new Uint8Array(WW * H);
const xyToId = new Int16Array(WW * H).fill(-1);
const flat = (x, y) => y * WW + x;
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
console.log('N', N, 'boxes', boxes, 'goals', goals, 'P', sx, sy);

// check if start boxes on dead
const { solve, heuristic, startMask, NB } = buildSolver(levelRows);
console.log('NB', NB, 'h0', heuristic(startMask));

// Use a patched approach: run with logging by forking solve logic
// Instead instrument via eval of children count
const fs = require('fs');
const src = fs.readFileSync(__dirname + '/solver_opt.js', 'utf8');
// manual: call solve with big timeout and see - already know fails

// Direct duplicate of legal push gen
const DX = [0,0,-1,1], DY = [-1,1,0,0];
const neigh = Array.from({length:N},()=>[]);
const pushTo = Array.from({length:N},()=>[-1,-1,-1,-1]);
const pushFrom = Array.from({length:N},()=>[-1,-1,-1,-1]);
for (let i = 0; i < N; i++) {
  const x = cellX[i], y = cellY[i];
  for (let d = 0; d < 4; d++) {
    const nx = x+DX[d], ny = y+DY[d];
    if (nx<0||ny<0||nx>=WW||ny>=H||wall[flat(nx,ny)]) continue;
    const nid = xyToId[flat(nx,ny)];
    if (nid < 0) continue;
    neigh[i].push(nid);
    const fx = x-DX[d], fy = y-DY[d];
    if (fx<0||fy<0||fx>=WW||fy>=H||wall[flat(fx,fy)]) continue;
    const fid = xyToId[flat(fx,fy)];
    if (fid < 0) continue;
    pushTo[i][d] = nid;
    pushFrom[i][d] = fid;
  }
}

// reverse dead
const dead = new Uint8Array(N);
const isGoal = new Uint8Array(N);
goals.forEach(g => isGoal[g]=1);
const goalDist = new Int16Array(N).fill(32000);
{
  const q = [...goals];
  goals.forEach(g => goalDist[g]=0);
  const alive = new Uint8Array(N);
  goals.forEach(g => alive[g]=1);
  for (let qi=0;qi<q.length;qi++) {
    const t=q[qi]; const x=cellX[t],y=cellY[t],bd=goalDist[t];
    for (let d=0;d<4;d++) {
      const Fx=x-DX[d],Fy=y-DY[d],Px=x-2*DX[d],Py=y-2*DY[d];
      if (Fx<0||Fy<0||Fx>=WW||Fy>=H||wall[flat(Fx,Fy)]) continue;
      if (Px<0||Py<0||Px>=WW||Py>=H||wall[flat(Px,Py)]) continue;
      const fid=xyToId[flat(Fx,Fy)];
      if (fid<0) continue;
      if (goalDist[fid]>bd+1){goalDist[fid]=bd+1;alive[fid]=1;q.push(fid);}
    }
  }
  for (let i=0;i<N;i++) {
    if (isGoal[i]) continue;
    if (!alive[i]) dead[i]=1;
  }
  console.log('dead count', [...dead].filter(x=>x).length);
  console.log('box dead?', boxes.map(b=>({b, pos:[cellX[b],cellY[b]], dead:!!dead[b], gd:goalDist[b]})));
}

// reach from player
const mask = boxes.reduce((m,b)=>m|(1n<<BigInt(b)),0n);
const reach = new Set();
const qq = [xyToId[flat(sx,sy)]];
reach.add(qq[0]);
for (let i=0;i<qq.length;i++) {
  for (const n of neigh[qq[i]]) {
    if (!reach.has(n) && (mask & (1n<<BigInt(n)))===0n) { reach.add(n); qq.push(n); }
  }
}
console.log('reach size', reach.size);

let legal=0;
for (const b of boxes) {
  for (let d=0;d<4;d++) {
    const to=pushTo[b][d], from=pushFrom[b][d];
    if (to<0) continue;
    if ((mask & (1n<<BigInt(to)))!==0n) continue;
    if (!reach.has(from)) continue;
    const isDead = dead[to];
    console.log('push', [cellX[b],cellY[b]], 'd',d, 'to',[cellX[to],cellY[to]], 'from',[cellX[from],cellY[from]], 'deadTo',!!isDead);
    if (!isDead) legal++;
  }
}
console.log('legal non-dead', legal);
