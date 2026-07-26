const L = require('../../levels.json');
function floors(p) {
  let n = 0, W = 0;
  p.forEach(r => { W = Math.max(W, r.length); });
  p.forEach(r => {
    const row = r.padEnd(W, '#');
    for (const c of row) if (c !== '#') n++;
  });
  return n;
}
const no = L.filter(l => !l.solution).map(l => {
  let b = 0;
  l.puzzle.forEach(r => { for (const c of r) if (c === '$' || c === '*') b++; });
  return { id: l.id, name: l.name, boxes: b, floors: floors(l.puzzle) };
}).sort((a, b) => a.boxes - b.boxes || a.floors - b.floors || a.id - b.id);

console.log('unsolved', no.length);
console.log('max floors', Math.max(...no.map(x => x.floors)));
console.log('floors<=62', no.filter(x => x.floors <= 62).length);
console.log('floors<=128', no.filter(x => x.floors <= 128).length);
console.log('floors<=256', no.filter(x => x.floors <= 256).length);
console.log('easiest 20:');
no.slice(0, 20).forEach(x => console.log(x.id, x.name, 'boxes=' + x.boxes, 'floors=' + x.floors));
