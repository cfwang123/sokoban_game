// 列出无答案关卡，按箱子数升序
const L = require('../../levels.json');
const todo = L.filter(l => !l.solution).map(l => {
  let b = 0;
  l.puzzle.forEach(r => {
    for (const c of r) if (c === '$' || c === '*') b++;
  });
  return { id: l.id, name: l.name, boxes: b };
}).sort((a, b) => a.boxes - b.boxes || a.id - b.id);
console.log(JSON.stringify(todo));
