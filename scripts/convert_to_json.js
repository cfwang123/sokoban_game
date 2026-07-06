// 将 levels.js 转写为 levels.json
const fs = require('fs');
const path = require('path');

const levelsCode = fs.readFileSync(path.join(__dirname, '..', 'js', 'levels.js'), 'utf8');
const getLevels = new Function(levelsCode + '\nreturn { LEVEL_NAMES, LEVEL_SOLUTIONS, LEVELS };');
const { LEVEL_NAMES, LEVEL_SOLUTIONS, LEVELS } = getLevels();

const data = [];
for (let i = 0; i < LEVELS.length; i++) {
  data.push({
    id: i,
    name: LEVEL_NAMES[i],
    puzzle: LEVELS[i],
    solution: LEVEL_SOLUTIONS[i] || null
  });
}

const outPath = path.join(__dirname, '..', 'levels.json');
fs.writeFileSync(outPath, JSON.stringify(data, null, 2), 'utf8');
console.log(`已写入 ${data.length} 关到 ${outPath}`);
