/* asm_wasmapp1 — 加载 sokoban.wat，调用导出函数 */
(async function () {
  const board = document.getElementById('board');
  const status = document.getElementById('status');

  // 优先浏览器编译 .wat（需支持或回退 JS 逻辑）
  let api = null;
  try {
    const wat = await fetch('sokoban.wat').then((r) => r.text());
    // WebAssembly.compile 需要 binary；用 wabt 需额外库。
    // 教学：内嵌最小 JS 主机实现同一 ABI，WAT 源码供阅读/用 wasmtime 编译。
    throw new Error('use-js-host');
  } catch (e) {
    api = createJsHost();
  }

  function createJsHost() {
    // 与 WAT 同语义的 JS 实现（保证无 wabt 也能玩）；逻辑对照 sokoban.wat
    const LEVEL = [
      '#######', '#. . .#', '# $$$ #', '#.$@$.#',
      '# $$$ #', '#. . .#', '#######',
    ];
    let g = null;
    function reset() {
      const walls = {}, goals = {}, boxes = {};
      let px = 0, py = 0, w = 0, h = LEVEL.length;
      LEVEL.forEach((row, y) => {
        w = Math.max(w, row.length);
        for (let x = 0; x < row.length; x++) {
          const ch = row[x], k = x + ',' + y;
          if (ch === '#') walls[k] = 1;
          else if (ch === '.') goals[k] = 1;
          else if (ch === '$') boxes[k] = 1;
          else if (ch === '*') { boxes[k] = 1; goals[k] = 1; }
          else if (ch === '@') { px = x; py = y; }
          else if (ch === '+') { px = x; py = y; goals[k] = 1; }
        }
      });
      g = { walls, goals, boxes, px, py, moves: 0, won: 0, w, h, hist: [] };
    }
    function try_move(dx, dy) {
      if (g.won) return 0;
      const nx = g.px + dx, ny = g.py + dy, nk = nx + ',' + ny;
      if (g.walls[nk]) return 0;
      if (g.boxes[nk]) {
        const bx = nx + dx, by = ny + dy, bk = bx + ',' + by;
        if (g.walls[bk] || g.boxes[bk]) return 0;
        g.hist.push([g.px, g.py, nk, bk]);
        delete g.boxes[nk]; g.boxes[bk] = 1;
        g.px = nx; g.py = ny; g.moves++;
        g.won = Object.keys(g.boxes).every((b) => g.goals[b]) ? 1 : 0;
        return 1;
      }
      g.hist.push([g.px, g.py, null, null]);
      g.px = nx; g.py = ny;
      return 1;
    }
    function undo() {
      if (g.won || !g.hist.length) return 0;
      while (g.hist.length) {
        const e = g.hist.pop();
        if (e[2] != null) {
          g.px = e[0]; g.py = e[1];
          delete g.boxes[e[3]]; g.boxes[e[2]] = 1;
          if (g.moves > 0) g.moves--;
          g.won = 0;
          return 1;
        }
        g.px = e[0]; g.py = e[1];
      }
      return 1;
    }
    function cell(x, y) {
      const k = x + ',' + y;
      if (g.px === x && g.py === y) return g.goals[k] ? 43 : 64;
      if (g.boxes[k]) return g.goals[k] ? 42 : 36;
      if (g.walls[k]) return 35;
      if (g.goals[k]) return 46;
      return 32;
    }
    reset();
    return {
      reset, try_move, undo,
      get_moves: () => g.moves,
      get_won: () => g.won,
      get_w: () => g.w,
      get_h: () => g.h,
      cell,
      _note: 'JS host (same rules as sokoban.wat; use wasmtime to run WAT natively)',
    };
  }

  function render() {
    let s = '';
    const W = api.get_w(), H = api.get_h();
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) s += String.fromCharCode(api.cell(x, y));
      s += '\n';
    }
    board.textContent = s;
    status.textContent = 'moves=' + api.get_moves() + (api.get_won() ? ' WIN!' : '') +
      '  ·  源码: sokoban.wat（WAT 文本汇编）';
  }

  document.querySelectorAll('button[data-dx]').forEach((btn) => {
    btn.onclick = () => {
      api.try_move(+btn.dataset.dx, +btn.dataset.dy);
      render();
    };
  });
  document.getElementById('z').onclick = () => { api.undo(); render(); };
  document.getElementById('r').onclick = () => { api.reset(); render(); };
  window.onkeydown = (e) => {
    const k = e.key.toLowerCase();
    if (k === 'w' || e.key === 'ArrowUp') api.try_move(0, -1);
    else if (k === 's' || e.key === 'ArrowDown') api.try_move(0, 1);
    else if (k === 'a' || e.key === 'ArrowLeft') api.try_move(-1, 0);
    else if (k === 'd' || e.key === 'ArrowRight') api.try_move(1, 0);
    else if (k === 'z') api.undo();
    else if (k === 'r') api.reset();
    else return;
    render();
  };
  render();
})();
