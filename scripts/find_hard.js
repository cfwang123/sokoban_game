// 找一道当前求解器 5 秒解不出的题（从难到易试，找到即停）
const path = require('path');
// reuse solver by requiring the build function - extract it
const fs = require('fs');
const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'levels.json'), 'utf8'));

// inline minimal call: spawn solver_opt via child for isolation
const { execFileSync } = require('child_process');

const unsolved = data.filter(l => !l.solution).map(l => {
  let b = 0;
  l.puzzle.forEach(r => { for (const c of r) if (c === '$' || c === '*') b++; });
  return { id: l.id, name: l.name, boxes: b };
}).sort((a, b) => b.boxes - a.boxes);

console.log('Trying hard unsolved levels (most boxes first), 5s limit each...\n');

for (const u of unsolved) {
  if (u.boxes < 6) break;
  process.stdout.write(`id=${u.id} ${u.name} boxes=${u.boxes} ... `);
  try {
    const out = execFileSync('node', [path.join(__dirname, 'solver_opt.js'), String(u.id), '5000'], {
      encoding: 'utf8',
      timeout: 15000
    });
    const lines = out.trim().split('\n');
    const last = lines.filter(l => l.startsWith('SOLVED') || l.startsWith('FAILED')).pop();
    console.log(last);
    if (last && last.startsWith('FAILED')) {
      console.log('\n>>> FOUND HARD LEVEL:', u.id, u.name);
      process.exit(0);
    }
  } catch (e) {
    console.log('ERROR/TIMEOUT', e.message.slice(0, 80));
    console.log('\n>>> FOUND HARD LEVEL (crash/timeout):', u.id, u.name);
    process.exit(0);
  }
}
console.log('All tested levels solved under 5s');
