// 将 SokWhole 和 SokEvo 的 txt 关卡文件转换为 JS 数组
// 运行: node convert_levels.js

const fs = require('fs');
const path = require('path');

function parseLevelFile(filePath) {
  const text = fs.readFileSync(filePath, 'utf8');
  const lines = text.split('\n');
  
  const levels = [];
  let currentLevel = [];
  let currentName = '';
  let inLevel = false;

  for (const line of lines) {
    const trimmed = line.trimEnd();

    // 注释行 → 记录关卡名
    if (trimmed.startsWith(';')) {
      const name = trimmed.slice(1).trim();
      if (name) currentName = name;
      // 结束当前关卡
      if (inLevel && currentLevel.length > 0) {
        levels.push({ name: currentName, rows: currentLevel });
        currentLevel = [];
        currentName = '';
        inLevel = false;
      }
      continue;
    }

    // 空行 → 结束当前关卡
    if (trimmed === '') {
      if (inLevel && currentLevel.length > 0) {
        levels.push({ name: currentName, rows: currentLevel });
        currentLevel = [];
        currentName = '';
        inLevel = false;
      }
      continue;
    }

    // 关卡行
    if (/^[#@\$\*\.\+\s-]+$/.test(trimmed) && trimmed.includes('#')) {
      currentLevel.push(trimmed);
      inLevel = true;
    } else {
      if (inLevel && currentLevel.length > 0) {
        levels.push({ name: currentName, rows: currentLevel });
        currentLevel = [];
        currentName = '';
        inLevel = false;
      }
    }
  }

  if (inLevel && currentLevel.length > 0) {
    levels.push({ name: currentName, rows: currentLevel });
  }

  return levels;
}

// 解析两个文件
const sokwhole = parseLevelFile(path.join(__dirname, 'sokwhole.txt'));
const sokevo = parseLevelFile(path.join(__dirname, 'sokevo.txt'));

console.log('SokWhole 关卡数:', sokwhole.length);
console.log('SokEvo 关卡数:', sokevo.length);
console.log('总计:', sokwhole.length + sokevo.length);

// 生成 JS 代码
let code = '// 推箱子关卡集：SokWhole (' + sokwhole.length + ') + SokEvo (' + sokevo.length + ') = ' + (sokwhole.length + sokevo.length) + ' 关\n';
code += '// 来源: Lee J Haywood (https://ljhaywood.uk/games/sokoban/)\n';
code += '// SokWhole 按最少推动数排序，从 1 推到高难度，逐步递增\n';
code += '// # 墙  空格 地板  . 目标  $ 箱子  * 箱子在目标上  @ 玩家  + 玩家在目标上\n\n';
code += '// 关卡名称数组，与 LEVELS_RAW 一一对应\n';
code += 'const LEVEL_NAMES = [\n';

// SokWhole names
code += '  // === SokWhole ===\n';
for (let i = 0; i < sokwhole.length; i++) {
  const name = sokwhole[i].name || ('SokWhole ' + (i + 1));
  code += '  "' + name + '"' + (i < sokwhole.length + sokevo.length - 1 ? ',' : '') + '\n';
}

// SokEvo names
code += '  // === SokEvo ===\n';
for (let i = 0; i < sokevo.length; i++) {
  const name = sokevo[i].name || ('SokEvo ' + (i + 1));
  code += '  "' + name + '"' + (sokwhole.length + i < sokwhole.length + sokevo.length - 1 ? ',' : '') + '\n';
}

code += '];\n\n';
code += 'const LEVELS_RAW = [\n';

function formatLevel(rows, idx, total) {
  const rowStrs = rows.map(r => '"' + r + '"');
  return '  [' + rowStrs.join(',') + ']' + (idx < total - 1 ? ',' : '') + '\n';
}

// SokWhole
code += '  // === SokWhole ===\n';
for (let i = 0; i < sokwhole.length; i++) {
  code += formatLevel(sokwhole[i].rows, i, sokwhole.length + sokevo.length);
}

// SokEvo
code += '  // === SokEvo ===\n';
for (let i = 0; i < sokevo.length; i++) {
  code += formatLevel(sokevo[i].rows, sokwhole.length + i, sokwhole.length + sokevo.length);
}

code += '];\n\n';
code += '// 转换为 LEVELS 数组（将空格替换为 \'-\' 以保持对齐）\n';
code += 'const LEVELS = LEVELS_RAW.map(rows =>\n';
code += '  rows.map(row => row.replace(/ /g, \'-\'))\n';
code += ');\n';

fs.writeFileSync(path.join(__dirname, 'js', 'levels.js'), code, 'utf8');
console.log('已生成 js/levels.js');
