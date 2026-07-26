/**
 * 从简单到难继续解无答案关卡（时间不限，每关独立子进程）
 * 用法: node scripts/cpp_solver/batch_continue.js
 *
 * 崩溃/失败会跳过继续；已有答案自动 skip。
 */
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '../..');
// prefer multi-thread binary
const exeMt = path.join(__dirname, process.platform === 'win32' ? 'sokosolve_mt.exe' : 'sokosolve_mt');
const exeSt = path.join(__dirname, process.platform === 'win32' ? 'sokosolve.exe' : 'sokosolve');
const exe = fs.existsSync(exeMt) ? exeMt : exeSt;
const logPath = path.join(__dirname, 'batch_continue_log.txt');
const levelsPath = path.join(root, 'levels.json');
const failPath = path.join(__dirname, 'batch_failed_ids.txt');

function log(msg) {
  const line = `[${new Date().toISOString().slice(11, 19)}] ${msg}`;
  console.log(line);
  try { fs.appendFileSync(logPath, line + '\n', 'utf8'); } catch (_) {}
}

function loadLevels() {
  return JSON.parse(fs.readFileSync(levelsPath, 'utf8'));
}

function loadUnsolved() {
  return loadLevels().filter(l => !l.solution).map(l => {
    let boxes = 0, floors = 0, W = 0;
    l.puzzle.forEach(r => { W = Math.max(W, r.length); });
    l.puzzle.forEach(r => {
      const row = r.padEnd(W, '#');
      for (const c of row) {
        if (c !== '#') floors++;
        if (c === '$' || c === '*') boxes++;
      }
    });
    return { id: l.id, name: l.name, boxes, floors };
  }).sort((a, b) => a.boxes - b.boxes || a.floors - b.floors || a.id - b.id);
}

function countUnsolved() {
  return loadLevels().filter(l => !l.solution).length;
}

function loadFailSet() {
  const s = new Set();
  if (fs.existsSync(failPath)) {
    for (const line of fs.readFileSync(failPath, 'utf8').split(/\r?\n/)) {
      const id = parseInt(line.trim(), 10);
      if (!isNaN(id)) s.add(id);
    }
  }
  return s;
}

function appendFail(id, reason) {
  fs.appendFileSync(failPath, `${id}\t${reason}\t${new Date().toISOString()}\n`, 'utf8');
}

if (!fs.existsSync(exe)) {
  console.error('Missing', exe);
  process.exit(1);
}

// 追加日志，不截断历史
fs.appendFileSync(logPath, `\n=== batch continue ${new Date().toISOString()} ===\n`, 'utf8');

let todo = loadUnsolved();
const prevFail = loadFailSet();
// 上次秒级失败的放到队尾，避免卡在 Laura 类
const hard = todo.filter(x => prevFail.has(x.id));
const easy = todo.filter(x => !prevFail.has(x.id));
todo = easy.concat(hard);

log(`Unsolved: ${todo.length} (deferred fails: ${hard.length})`);

let solved = 0, failed = 0, skipped = 0;

for (let i = 0; i < todo.length; i++) {
  const item = todo[i];

  // 实时刷新：已解则跳过
  const cur = loadLevels().find(x => x.id === item.id);
  if (cur && cur.solution) {
    log(`[skip] id=${item.id} ${item.name} already solved`);
    skipped++;
    continue;
  }

  log(`>>> [${i + 1}/${todo.length}] boxes=${item.boxes} floors=${item.floors} id=${item.id} ${item.name}`);

  let r;
  try {
    r = spawnSync(exe, [String(item.id), '0', 'auto', '--write'], {
      cwd: root,
      encoding: 'utf8',
      maxBuffer: 80 * 1024 * 1024,
      windowsHide: true,
    });
  } catch (e) {
    failed++;
    log(`CRASH id=${item.id} ${e.message}`);
    appendFail(item.id, 'exception:' + e.message);
    continue;
  }

  const out = ((r && r.stdout) || '') + ((r && r.stderr) || '');
  try { fs.appendFileSync(logPath, out + '\n', 'utf8'); } catch (_) {}

  const lines = out.trim().split(/\r?\n/);
  lines.slice(-10).forEach(l => console.log(l));

  if (r.signal) {
    failed++;
    log(`KILL id=${item.id} signal=${r.signal}`);
    appendFail(item.id, 'signal:' + r.signal);
  } else if (/SOLVED/.test(out)) {
    solved++;
    log(`OK id=${item.id} ${item.name}`);
  } else if (/already solved/i.test(out)) {
    skipped++;
    log(`SKIP id=${item.id}`);
  } else {
    failed++;
    log(`FAIL id=${item.id} exit=${r.status}`);
    appendFail(item.id, 'exit:' + r.status);
  }

  const left = countUnsolved();
  log(`--- solved=${solved} failed=${failed} skipped=${skipped} remaining=${left} ---`);

  if ((solved + failed) % 3 === 0 || left === 0) {
    spawnSync(process.execPath, [path.join(root, 'scripts/gen_levels_js.js')], {
      cwd: root, encoding: 'utf8', windowsHide: true,
    });
    log('synced HTML');
  }
}

spawnSync(process.execPath, [path.join(root, 'scripts/gen_levels_js.js')], {
  cwd: root, encoding: 'utf8', windowsHide: true,
});
log(`=== DONE solved=${solved} failed=${failed} skipped=${skipped} remaining=${countUnsolved()} ===`);
