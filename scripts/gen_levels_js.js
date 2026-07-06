// 从 levels.json 生成 levels_data.js（单个大数组，元素为 { name, puzzle, solution }）
const fs = require('fs');
const path = require('path');

const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'levels.json'), 'utf8'));

const items = data.map(d => ({
  name: d.name,
  puzzle: d.puzzle,
  solution: d.solution || ''
}));

const js = `// 自动生成 - 从 levels.json 转换
window.LEVELS_DATA = ${JSON.stringify(items)};`;

fs.writeFileSync(path.join(__dirname, '..', 'js', 'levels_data.js'), js, 'utf8');
console.log('已生成 js/levels_data.js');
