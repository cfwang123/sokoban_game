const level = require('../levels.json').find(l => l.id === 75);
const rows = level.puzzle;
const H = rows.length;
const WW = Math.max(...rows.map(r => r.length));
const pad = rows.map(r => r.padEnd(WW, '#'));
console.log('size', WW, H);
pad.forEach(r => console.log(r));

const wall = new Set();
const floors = [];
const goals = [];
const boxes = [];
let P = null;
for (let y = 0; y < H; y++) {
  for (let x = 0; x < WW; x++) {
    const c = pad[y][x], k = x + ',' + y;
    if (c === '#') { wall.add(k); continue; }
    floors.push(k);
    if (c === '.' || c === '*' || c === '+') goals.push(k);
    if (c === '$' || c === '*') boxes.push(k);
    if (c === '@' || c === '+') P = { x, y };
  }
}
console.log('floors', floors.length, 'goals', goals.length, 'boxes', boxes, 'P', P);

const alive = new Set(goals);
const q = [...goals];
const D = [[0, -1], [0, 1], [-1, 0], [1, 0]];
for (let i = 0; i < q.length; i++) {
  const [x, y] = q[i].split(',').map(Number);
  for (const [dx, dy] of D) {
    const Fx = x - dx, Fy = y - dy;
    const pEx = x + dx, pEy = y + dy;
    if (Fx < 0 || Fy < 0 || Fx >= WW || Fy >= H) continue;
    if (pEx < 0 || pEy < 0 || pEx >= WW || pEy >= H) continue;
    const fk = Fx + ',' + Fy, pk = pEx + ',' + pEy;
    if (wall.has(fk) || wall.has(pk)) continue;
    if (!alive.has(fk)) { alive.add(fk); q.push(fk); }
  }
}
console.log('alive', alive.size, 'of', floors.length);
for (const b of boxes) console.log('box', b, 'alive', alive.has(b));

// Why did solver fail at 0ms?
// Import and add debug
const keyToId = new Map();
floors.forEach((k, i) => keyToId.set(k, i));
console.log('start player key', P.x + ',' + P.y, 'id', keyToId.get(P.x + ',' + P.y));
