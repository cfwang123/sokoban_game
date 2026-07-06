// 测试指定关卡是否可解
const fs = require('fs');
const path = require('path');

const levelsCode = fs.readFileSync(path.join(__dirname, 'js', 'levels.js'), 'utf8');
const startRaw = levelsCode.indexOf('const LEVELS_RAW = [');
let depth = 0, endRaw;
for (let i = startRaw; i < levelsCode.length; i++) {
  if (levelsCode[i] === '[') depth++;
  else if (levelsCode[i] === ']') { depth--; if (depth === 0) { endRaw = i + 1; break; } }
}
let LEVELS_RAW;
eval('LEVELS_RAW = ' + levelsCode.slice(startRaw + 'const LEVELS_RAW = '.length, endRaw));
const LEVELS = LEVELS_RAW.map(rows => rows.map(row => row.replace(/ /g, '-')));

// 测试 SokWhole 17 L (index 32)
const level = LEVELS[32];
console.log('Level 32 (17 L):');
level.forEach(r => console.log('  ' + r));

// 解析
const walls = new Set(), goals = new Set(), boxes = new Set();
let player = null;
for (let y = 0; y < level.length; y++) {
  for (let x = 0; x < level[y].length; x++) {
    const ch = level[y][x], key = x + ',' + y;
    if (ch === '#') walls.add(key);
    else if (ch === '.') goals.add(key);
    else if (ch === '$') boxes.add(key);
    else if (ch === '*') { boxes.add(key); goals.add(key); }
    else if (ch === '@') player = {x,y};
    else if (ch === '+') { player = {x,y}; goals.add(key); }
  }
}
console.log('Boxes:', boxes.size, 'Goals:', goals.size);

// 求解
function isDeadlocked(boxKey, w, g) {
  if (g.has(boxKey)) return false;
  const [x, y] = boxKey.split(',').map(Number);
  const u = w.has(x+','+(y-1)), d = w.has(x+','+(y+1));
  const l = w.has((x-1)+','+y), r = w.has((x+1)+','+y);
  return (u&&l)||(u&&r)||(d&&l)||(d&&r);
}
function stateKey(p, b) {
  return p.x+','+p.y+'|'+Array.from(b).sort().join(';');
}

const maxNodes = 3000000;
const dirs = [{dx:0,dy:-1},{dx:0,dy:1},{dx:-1,dy:0},{dx:1,dy:0}];
const q = [{player:{x:player.x,y:player.y},boxes:new Set(boxes),path:[]}];
const visited = new Set([stateKey(player, boxes)]);
let nodes = 0;

while (q.length > 0 && nodes < maxNodes) {
  const cur = q.shift();
  nodes++;
  let won = true;
  for (const b of cur.boxes) { if (!goals.has(b)) { won = false; break; } }
  if (won) {
    console.log('Solved! Nodes:', nodes, 'Steps:', cur.path.length);
    process.exit(0);
  }
  for (const d of dirs) {
    const nx = cur.player.x + d.dx, ny = cur.player.y + d.dy, nk = nx+','+ny;
    if (walls.has(nk)) continue;
    const nb = new Set(cur.boxes);
    if (cur.boxes.has(nk)) {
      const bx = nx+d.dx, by = ny+d.dy, bk = bx+','+by;
      if (walls.has(bk) || cur.boxes.has(bk)) continue;
      nb.delete(nk); nb.add(bk);
      if (isDeadlocked(bk, walls, goals)) continue;
    }
    const sk = stateKey({x:nx,y:ny}, nb);
    if (visited.has(sk)) continue;
    visited.add(sk);
    q.push({player:{x:nx,y:ny},boxes:nb,path:cur.path.concat([d])});
  }
}
console.log('Failed after', nodes, 'nodes');
