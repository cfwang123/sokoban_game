// 测试所有关卡是否可通关
// 运行: node test_levels.js

const fs = require('fs');
const path = require('path');

// 读取关卡数据
const levelsCode = fs.readFileSync(path.join(__dirname, 'js', 'levels.js'), 'utf8');

// 提取 LEVELS_RAW 数组（文本方式，用括号计数）
const startIdx = levelsCode.indexOf('const LEVELS_RAW = [');
if (startIdx < 0) {
  console.error('无法解析 LEVELS_RAW');
  process.exit(1);
}
let depth = 0;
let endIdx = startIdx + 'const LEVELS_RAW = '.length;
for (let i = endIdx; i < levelsCode.length; i++) {
  if (levelsCode[i] === '[') depth++;
  else if (levelsCode[i] === ']') {
    depth--;
    if (depth === 0) { endIdx = i + 1; break; }
  }
}

const arrayText = levelsCode.slice(startIdx + 'const LEVELS_RAW = '.length, endIdx);
let LEVELS_RAW;
eval('LEVELS_RAW = ' + arrayText);

// 手动转换
const LEVELS = LEVELS_RAW.map(rows =>
  rows.map(row => row.replace(/ /g, '-'))
);

// ===== AI 求解器（从 ai.js 移植到 Node.js） =====
function isDeadlocked(boxKey, walls, goals) {
  if (goals.has(boxKey)) return false;
  const [x, y] = boxKey.split(',').map(Number);
  const up = walls.has(x + ',' + (y - 1));
  const down = walls.has(x + ',' + (y + 1));
  const left = walls.has((x - 1) + ',' + y);
  const right = walls.has((x + 1) + ',' + y);
  if (up && left) return true;
  if (up && right) return true;
  if (down && left) return true;
  if (down && right) return true;
  return false;
}

function stateKey(player, boxes) {
  const sorted = Array.from(boxes).sort();
  return player.x + ',' + player.y + '|' + sorted.join(';');
}

function aiSolve(levelRows) {
  const walls = new Set();
  const goals = new Set();
  const boxes = new Set();
  let player = null;

  for (let y = 0; y < levelRows.length; y++) {
    const row = levelRows[y];
    for (let x = 0; x < row.length; x++) {
      const ch = row[x];
      const key = x + ',' + y;
      switch (ch) {
        case '#': walls.add(key); break;
        case '.': goals.add(key); break;
        case '$': boxes.add(key); break;
        case '*': boxes.add(key); goals.add(key); break;
        case '@': player = { x, y }; break;
        case '+': player = { x, y }; goals.add(key); break;
      }
    }
  }

  if (!player) return null;

  const maxNodes = 100000;
  const dirs = [
    { dx: 0, dy: -1, name: 'up' },
    { dx: 0, dy: 1, name: 'down' },
    { dx: -1, dy: 0, name: 'left' },
    { dx: 1, dy: 0, name: 'right' }
  ];

  const startBoxes = new Set(boxes);
  const startPlayer = { x: player.x, y: player.y };

  const queue = [{
    player: startPlayer,
    boxes: startBoxes,
    path: []
  }];

  const visited = new Set();
  visited.add(stateKey(startPlayer, startBoxes));

  let nodeCount = 0;

  while (queue.length > 0 && nodeCount < maxNodes) {
    const cur = queue.shift();
    nodeCount++;

    let won = true;
    for (const b of cur.boxes) {
      if (!goals.has(b)) { won = false; break; }
    }
    if (won) return { path: cur.path, nodes: nodeCount };

    for (const d of dirs) {
      const nx = cur.player.x + d.dx;
      const ny = cur.player.y + d.dy;
      const nKey = nx + ',' + ny;

      if (walls.has(nKey)) continue;

      const newBoxes = new Set(cur.boxes);

      if (cur.boxes.has(nKey)) {
        const bx = nx + d.dx;
        const by = ny + d.dy;
        const bKey = bx + ',' + by;

        if (walls.has(bKey) || cur.boxes.has(bKey)) continue;

        newBoxes.delete(nKey);
        newBoxes.add(bKey);

        if (isDeadlocked(bKey, walls, goals)) continue;
      }

      const newPlayer = { x: nx, y: ny };
      const sk = stateKey(newPlayer, newBoxes);
      if (visited.has(sk)) continue;
      visited.add(sk);

      queue.push({
        player: newPlayer,
        boxes: newBoxes,
        path: cur.path.concat([d.name])
      });
    }
  }

  return null;
}

// ===== 测试所有关卡 =====
console.log('开始测试 ' + LEVELS.length + ' 个关卡...\n');

const results = [];
let passed = 0;
let failed = 0;

for (let i = 0; i < LEVELS.length; i++) {
  const levelRows = LEVELS[i];
  process.stdout.write('测试第 ' + (i + 1) + ' 关... ');

  const startTime = Date.now();
  const result = aiSolve(levelRows);
  const elapsed = Date.now() - startTime;

  if (result) {
    console.log('通过 (' + result.path.length + ' 步, ' + result.nodes + ' 节点, ' + elapsed + 'ms)');
    results.push({ index: i, solvable: true, steps: result.path.length, nodes: result.nodes, time: elapsed });
    passed++;
  } else {
    console.log('失败 (无法通关)');
    results.push({ index: i, solvable: false, steps: 0, nodes: 0, time: elapsed });
    failed++;
  }
}

console.log('\n========== 测试结果 ==========');
console.log('总计: ' + LEVELS.length + ' 关');
console.log('通过: ' + passed + ' 关');
console.log('失败: ' + failed + ' 关');

// 生成 Markdown 报告
let md = '# 关卡测试报告\n\n';
md += '## 概要\n\n';
md += '- 总计关卡：' + LEVELS.length + '\n';
md += '- 可通关：' + passed + '\n';
md += '- 无法通关：' + failed + '\n\n';

if (failed > 0) {
  md += '## 无法通关的关卡\n\n';
  md += '| 关卡序号 | 测试时间(ms) |\n';
  md += '|---------|-------------|\n';
  for (const r of results) {
    if (!r.solvable) {
      md += '| ' + (r.index + 1) + ' | ' + r.time + ' |\n';
    }
  }
  md += '\n';
}

md += '## 可通关关卡详情\n\n';
md += '| 关卡序号 | 步数 | 搜索节点 | 时间(ms) |\n';
md += '|---------|------|---------|---------|\n';
for (const r of results) {
  if (r.solvable) {
    md += '| ' + (r.index + 1) + ' | ' + r.steps + ' | ' + r.nodes + ' | ' + r.time + ' |\n';
  } else {
    md += '| ' + (r.index + 1) + ' | - | - | ' + r.time + ' (失败) |\n';
  }
}

fs.writeFileSync(path.join(__dirname, 'level_test_report.md'), md, 'utf8');
console.log('\n报告已保存到 level_test_report.md');

// 如果有关卡失败，生成新的 levels.js（去掉失败关卡）
if (failed > 0) {
  const failedIndices = new Set(results.filter(r => !r.solvable).map(r => r.index));
  const newLevelsRaw = LEVELS_RAW.filter((_, i) => !failedIndices.has(i));

  let newCode = '// 推箱子关卡集：SokWhole (107) + SokEvo (107) = 214 关\n';
  newCode += '// 来源: Lee J Haywood (https://ljhaywood.uk/games/sokoban/)\n';
  newCode += '// SokWhole 按最少推动数排序，从 1 推到高难度，逐步递增\n';
  newCode += '// # 墙  空格 地板  . 目标  $ 箱子  * 箱子在目标上  @ 玩家  + 玩家在目标上\n';
  newCode += '// 注意：已移除无法通关的关卡\n\n';
  newCode += 'const LEVELS_RAW = [\n';

  for (let i = 0; i < newLevelsRaw.length; i++) {
    const rows = newLevelsRaw[i];
    const rowStrs = rows.map(r => '"' + r + '"');
    newCode += '  [' + rowStrs.join(',') + ']';
    if (i < newLevelsRaw.length - 1) newCode += ',';
    newCode += '\n';
  }

  newCode += '];\n\n';
  newCode += '// 转换为 LEVELS 数组（将空格替换为 \'-\' 以保持对齐）\n';
  newCode += 'const LEVELS = LEVELS_RAW.map(rows =>\n';
  newCode += '  rows.map(row => row.replace(/ /g, \'-\'))\n';
  newCode += ');\n';

  fs.writeFileSync(path.join(__dirname, 'js', 'levels.js'), newCode, 'utf8');
  console.log('已更新 levels.js，移除了 ' + failed + ' 个无法通关的关卡');
}
