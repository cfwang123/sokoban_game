// ===== 推箱子核心游戏引擎 =====

const CELL = 40;
const PADDING = 20;
const ANIM_INTERVAL = 60; // 寻路/AI 每步间隔 ms
const HOLD_DELAY = 180;   // 按住方向键首次延迟 ms
const HOLD_INTERVAL = 90; // 按住后重复间隔 ms

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const levelSelect = document.getElementById('levelSelect');
const moveCountEl = document.getElementById('moveCount');
const undoBtn = document.getElementById('undoBtn');
const resetBtn = document.getElementById('resetBtn');
const viewAnswerBtn = document.getElementById('viewAnswerBtn');
const aiStatus = document.getElementById('aiStatus');
const winOverlay = document.getElementById('winOverlay');
const winMoves = document.getElementById('winMoves');
const nextLevelBtn = document.getElementById('nextLevelBtn');

// ---- 游戏状态 ----
let state = null;
let animQueue = [];        // 方向队列（寻路/AI 用）
let animTimer = null;
let inputLocked = false;   // 动画执行期间锁定输入
let holdTimer = null;      // 按住方向键定时器
let holdDir = null;        // 当前按住的方向
let aiActive = false;

// ---- 关卡管理 ----
function populateLevelSelect() {
  levelSelect.innerHTML = '';
  for (let i = 0; i < LEVELS_DATA.length; i++) {
    const opt = document.createElement('option');
    opt.value = i;
    const name = LEVELS_DATA[i].name || '';
    opt.textContent = '第' + (i + 1) + '关' + (name ? ' - ' + name : '');
    levelSelect.appendChild(opt);
  }
}

function getLastLevel() {
  const saved = localStorage.getItem('sokoban_last_level');
  if (saved !== null) {
    const n = parseInt(saved, 10);
    if (!isNaN(n) && n >= 0 && n < LEVELS_DATA.length) return n;
  }
  return 0;
}

function saveLastLevel(index) {
  localStorage.setItem('sokoban_last_level', String(index));
}

// ---- 解析关卡 ----
function parseLevel(index) {
  const raw = LEVELS_DATA[index].puzzle;
  const walls = new Set();
  const goals = new Set();
  const boxes = new Set();
  let player = null;

  for (let y = 0; y < raw.length; y++) {
    const row = raw[y];
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

  return { walls, goals, boxes, player, index };
}

function loadLevel(index) {
  stopAI();
  clearAnimQueue();
  const parsed = parseLevel(index);
  state = {
    walls: parsed.walls,
    goals: parsed.goals,
    boxes: parsed.boxes,
    player: parsed.player,
    moves: 0,
    history: [],
    won: false,
    levelIndex: index
  };
  saveLastLevel(index);
  levelSelect.value = index;
  updateUI();
  resizeCanvas();
  render();
  winOverlay.classList.add('hidden');
}

function resetLevel() {
  if (!state) return;
  stopAI();
  clearAnimQueue();
  loadLevel(state.levelIndex);
}

// ---- Canvas 尺寸 ----
function resizeCanvas() {
  if (!state) return;
  let maxX = 0, maxY = 0;
  for (const key of state.walls) {
    const [x, y] = key.split(',').map(Number);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
  }
  for (const key of state.goals) {
    const [x, y] = key.split(',').map(Number);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
  }
  for (const key of state.boxes) {
    const [x, y] = key.split(',').map(Number);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
  }
  if (state.player) {
    maxX = Math.max(maxX, state.player.x);
    maxY = Math.max(maxY, state.player.y);
  }
  canvas.width = (maxX + 1) * CELL + PADDING * 2;
  canvas.height = (maxY + 1) * CELL + PADDING * 2;
}

// ---- 渲染 ----
function render() {
  if (!state) return;
  const ctx2 = ctx;
  const w = canvas.width;
  const h = canvas.height;

  ctx2.clearRect(0, 0, w, h);

  // 绘制网格
  const offsetX = PADDING;
  const offsetY = PADDING;

  // 计算关卡边界
  let maxX = 0, maxY = 0;
  for (const key of state.walls) {
    const [x, y] = key.split(',').map(Number);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
  }
  for (const key of state.goals) {
    const [x, y] = key.split(',').map(Number);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
  }
  for (const key of state.boxes) {
    const [x, y] = key.split(',').map(Number);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
  }
  if (state.player) {
    maxX = Math.max(maxX, state.player.x);
    maxY = Math.max(maxY, state.player.y);
  }

  // 绘制所有地板（全覆盖关卡范围）
  for (let y = 0; y <= maxY; y++) {
    for (let x = 0; x <= maxX; x++) {
      const px = offsetX + x * CELL;
      const py = offsetY + y * CELL;
      ctx2.fillStyle = '#3a3a55';
      ctx2.fillRect(px, py, CELL, CELL);
      ctx2.strokeStyle = '#444466';
      ctx2.lineWidth = 0.5;
      ctx2.strokeRect(px, py, CELL, CELL);
    }
  }

  // 墙
  for (const key of state.walls) {
    const [x, y] = key.split(',').map(Number);
    const px = offsetX + x * CELL;
    const py = offsetY + y * CELL;
    ctx2.fillStyle = '#4a4a6a';
    ctx2.fillRect(px, py, CELL, CELL);
    // 高光
    ctx2.fillStyle = '#5a5a7a';
    ctx2.fillRect(px, py, CELL, 3);
    ctx2.fillRect(px, py, 3, CELL);
    // 阴影
    ctx2.fillStyle = '#2a2a4a';
    ctx2.fillRect(px, py + CELL - 3, CELL, 3);
    ctx2.fillRect(px + CELL - 3, py, 3, CELL);
  }

  // 目标点
  for (const key of state.goals) {
    const [x, y] = key.split(',').map(Number);
    const px = offsetX + x * CELL + CELL / 2;
    const py = offsetY + y * CELL + CELL / 2;
    ctx2.beginPath();
    ctx2.arc(px, py, 6, 0, Math.PI * 2);
    ctx2.fillStyle = '#e94560';
    ctx2.fill();
    ctx2.strokeStyle = '#ff6b81';
    ctx2.lineWidth = 2;
    ctx2.stroke();
  }

  // 箱子
  for (const key of state.boxes) {
    const [x, y] = key.split(',').map(Number);
    const px = offsetX + x * CELL + 4;
    const py = offsetY + y * CELL + 4;
    const size = CELL - 8;
    const onGoal = state.goals.has(key);

    ctx2.fillStyle = onGoal ? '#2ecc71' : '#f39c12';
    ctx2.fillRect(px, py, size, size);
    ctx2.strokeStyle = onGoal ? '#27ae60' : '#e67e22';
    ctx2.lineWidth = 2;
    ctx2.strokeRect(px, py, size, size);

    // 箱子高光
    ctx2.fillStyle = onGoal ? '#58d68d' : '#f5b041';
    ctx2.fillRect(px + 2, py + 2, size - 4, 3);
    ctx2.fillRect(px + 2, py + 2, 3, size - 4);

    // 箱子上的十字标记
    ctx2.strokeStyle = onGoal ? '#1e8449' : '#d35400';
    ctx2.lineWidth = 1.5;
    const cx = px + size / 2;
    const cy = py + size / 2;
    ctx2.beginPath();
    ctx2.moveTo(cx - 6, cy);
    ctx2.lineTo(cx + 6, cy);
    ctx2.moveTo(cx, cy - 6);
    ctx2.lineTo(cx, cy + 6);
    ctx2.stroke();
  }

  // 玩家
  if (state.player) {
    const px = offsetX + state.player.x * CELL + CELL / 2;
    const py = offsetY + state.player.y * CELL + CELL / 2;
    const r = CELL * 0.35;

    // 身体
    ctx2.beginPath();
    ctx2.arc(px, py, r, 0, Math.PI * 2);
    ctx2.fillStyle = '#3498db';
    ctx2.fill();
    ctx2.strokeStyle = '#2980b9';
    ctx2.lineWidth = 2;
    ctx2.stroke();

    // 眼睛（朝向）
    ctx2.fillStyle = '#fff';
    ctx2.beginPath();
    ctx2.arc(px - 4, py - 3, 3, 0, Math.PI * 2);
    ctx2.fill();
    ctx2.beginPath();
    ctx2.arc(px + 4, py - 3, 3, 0, Math.PI * 2);
    ctx2.fill();

    ctx2.fillStyle = '#1a1a2e';
    ctx2.beginPath();
    ctx2.arc(px - 4, py - 3, 1.5, 0, Math.PI * 2);
    ctx2.fill();
    ctx2.beginPath();
    ctx2.arc(px + 4, py - 3, 1.5, 0, Math.PI * 2);
    ctx2.fill();
  }
}

// ---- 移动逻辑 ----
function tryMove(dx, dy) {
  if (!state || state.won || inputLocked) return false;

  const nx = state.player.x + dx;
  const ny = state.player.y + dy;
  const nKey = nx + ',' + ny;

  // 撞墙
  if (state.walls.has(nKey)) return false;

  // 推箱子
  if (state.boxes.has(nKey)) {
    const bx = nx + dx;
    const by = ny + dy;
    const bKey = bx + ',' + by;

    if (state.walls.has(bKey) || state.boxes.has(bKey)) return false;

    // 保存历史（用于撤销）
    const histEntry = {
      player: { x: state.player.x, y: state.player.y },
      boxMoved: { from: nKey, to: bKey }
    };
    state.history.push(histEntry);

    state.boxes.delete(nKey);
    state.boxes.add(bKey);
    state.player.x = nx;
    state.player.y = ny;
    state.moves++;
    updateUI();
    render();
    checkWin();
    return true;
  }

  // 普通移动（不计步数）
  const histEntry = {
    player: { x: state.player.x, y: state.player.y },
    boxMoved: null
  };
  state.history.push(histEntry);

  state.player.x = nx;
  state.player.y = ny;
  updateUI();
  render();
  return true;
}

// 不渲染的移动（用于鼠标点击寻路，批量执行后一次渲染）
function tryMoveInstant(dx, dy) {
  if (!state || state.won) return false;

  const nx = state.player.x + dx;
  const ny = state.player.y + dy;
  const nKey = nx + ',' + ny;

  if (state.walls.has(nKey)) return false;

  if (state.boxes.has(nKey)) {
    const bx = nx + dx;
    const by = ny + dy;
    const bKey = bx + ',' + by;
    if (state.walls.has(bKey) || state.boxes.has(bKey)) return false;

    const histEntry = {
      player: { x: state.player.x, y: state.player.y },
      boxMoved: { from: nKey, to: bKey }
    };
    state.history.push(histEntry);

    state.boxes.delete(nKey);
    state.boxes.add(bKey);
    state.player.x = nx;
    state.player.y = ny;
    state.moves++;
    checkWin();
    return true;
  }

  const histEntry = {
    player: { x: state.player.x, y: state.player.y },
    boxMoved: null
  };
  state.history.push(histEntry);

  state.player.x = nx;
  state.player.y = ny;
  return true;
}

function undo() {
  if (!state || state.won || inputLocked || state.history.length === 0) return;
  // 跳过纯移动步骤，只撤销推箱子的步骤
  let entry = null;
  while (state.history.length > 0) {
    entry = state.history.pop();
    if (entry.boxMoved) break;
    // 纯移动：恢复玩家位置（不计步数）
    state.player = entry.player;
  }
  if (!entry || !entry.boxMoved) {
    updateUI();
    render();
    return;
  }
  state.player = entry.player;
  state.boxes.delete(entry.boxMoved.to);
  state.boxes.add(entry.boxMoved.from);
  state.moves--;
  updateUI();
  render();
}

function checkWin() {
  let won = true;
  for (const b of state.boxes) {
    if (!state.goals.has(b)) { won = false; break; }
  }
  if (won) {
    state.won = true;
    winMoves.textContent = '共用 ' + state.moves + ' 步完成！';
    winOverlay.classList.remove('hidden');
    stopAI();
  }
}

// ---- 动画队列（寻路/AI 用） ----
function clearAnimQueue() {
  animQueue = [];
  if (animTimer) {
    clearInterval(animTimer);
    animTimer = null;
  }
  inputLocked = false;
}

function hasLevelSolution(index) {
  return !!(LEVELS_DATA[index].solution && LEVELS_DATA[index].solution.trim());
}

function getAnswerQueue(index) {
  const solution = LEVELS_DATA[index].solution;
  if (!solution) return [];
  const queue = [];
  const charMap = {
    U: 'up',
    D: 'down',
    L: 'left',
    R: 'right'
  };

  for (const ch of solution) {
    const dir = charMap[ch.toUpperCase()];
    if (dir) queue.push(dir);
  }

  return queue;
}

function refreshAnswerUI() {
  if (!state) {
    viewAnswerBtn.disabled = true;
    viewAnswerBtn.textContent = '查看答案';
    viewAnswerBtn.classList.remove('active');
    aiStatus.textContent = '';
    return;
  }

  if (aiActive) {
    viewAnswerBtn.disabled = false;
    viewAnswerBtn.textContent = '停止查看';
    viewAnswerBtn.classList.add('active');
    return;
  }

  const hasSolution = hasLevelSolution(state.levelIndex);
  viewAnswerBtn.disabled = !hasSolution || state.won;
  viewAnswerBtn.textContent = '查看答案';
  viewAnswerBtn.classList.remove('active');
  if (state.won) {
    aiStatus.textContent = '已过关';
  } else {
    aiStatus.textContent = hasSolution ? '本关有答案' : '本关暂无答案';
  }
}

function startAnimQueue(queue) {
  clearAnimQueue();
  if (!queue || queue.length === 0) return;
  animQueue = queue;
  inputLocked = true;

  const dirMap = {
    up: { dx: 0, dy: -1 },
    down: { dx: 0, dy: 1 },
    left: { dx: -1, dy: 0 },
    right: { dx: 1, dy: 0 }
  };

  animTimer = setInterval(() => {
    if (animQueue.length === 0) {
      clearInterval(animTimer);
      animTimer = null;
      inputLocked = false;
      if (aiActive) stopAI();
      return;
    }
    const dir = animQueue.shift();
    const d = dirMap[dir];
    if (d) {
      tryMoveInstant(d.dx, d.dy);
      updateUI();
      render();
    }
  }, ANIM_INTERVAL);
}

// ---- 鼠标点击 Canvas ----
canvas.addEventListener('click', (e) => {
  if (!state || state.won || inputLocked || aiActive) return;

  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  const mx = (e.clientX - rect.left) * scaleX;
  const my = (e.clientY - rect.top) * scaleY;

  const gx = Math.floor((mx - PADDING) / CELL);
  const gy = Math.floor((my - PADDING) / CELL);
  const gKey = gx + ',' + gy;

  // 检查是否在有效范围内
  if (gx < 0 || gy < 0) return;

  // 点击玩家相邻的箱子 → 推 1 格
  if (state.boxes.has(gKey)) {
    const dx = gx - state.player.x;
    const dy = gy - state.player.y;
    // 必须是相邻（曼哈顿距离为1）
    if (Math.abs(dx) + Math.abs(dy) === 1) {
      tryMove(dx, dy);
    }
    return;
  }

  // 点击空地 → BFS 寻路，同步执行所有步
  if (!state.walls.has(gKey) && !state.boxes.has(gKey)) {
    const path = findPath(state, gx, gy);
    if (path && path.length > 0) {
      const dirMap = {
        up: { dx: 0, dy: -1 },
        down: { dx: 0, dy: 1 },
        left: { dx: -1, dy: 0 },
        right: { dx: 1, dy: 0 }
      };
      // 禁用渲染中间步骤，全部走完后一次渲染
      const origRender = render;
      render = function(){};
      for (const dir of path) {
        const d = dirMap[dir];
        if (d) tryMoveInstant(d.dx, d.dy);
        if (state.won) break;
      }
      render = origRender;
      updateUI();
      render();
    }
    return;
  }
});

function clearHold() {
  if (holdTimer) {
    clearTimeout(holdTimer);
    clearInterval(holdTimer);
    holdTimer = null;
  }
  holdDir = null;
}

// ---- 键盘 ----
const keyMap = {
  ArrowUp: { dx: 0, dy: -1 },
  ArrowDown: { dx: 0, dy: 1 },
  ArrowLeft: { dx: -1, dy: 0 },
  ArrowRight: { dx: 1, dy: 0 },
  w: { dx: 0, dy: -1 },
  W: { dx: 0, dy: -1 },
  s: { dx: 0, dy: 1 },
  S: { dx: 0, dy: 1 },
  a: { dx: -1, dy: 0 },
  A: { dx: -1, dy: 0 },
  d: { dx: 1, dy: 0 },
  D: { dx: 1, dy: 0 }
};

document.addEventListener('keydown', (e) => {
  // 快捷键：Z 撤销，R 重置，Space 下一关，F1 查看答案
  if (e.key === 'z' || e.key === 'Z') {
    e.preventDefault();
    undo();
    return;
  }
  if (e.key === 'r' || e.key === 'R') {
    e.preventDefault();
    resetLevel();
    return;
  }
  if (e.key === 'F1') {
    e.preventDefault();
    viewAnswerBtn.click();
    return;
  }
  if (e.key === ' ' || e.key === 'Space') {
    e.preventDefault();
    if (state && state.won) {
      const next = state.levelIndex + 1;
      if (next < LEVELS_DATA.length) {
        loadLevel(next);
      } else {
        winOverlay.classList.add('hidden');
      }
    }
    return;
  }
  if (e.key === 'PageUp') {
    e.preventDefault();
    if (!state) return;
    const prev = state.levelIndex - 1;
    if (prev >= 0) loadLevel(prev);
    return;
  }
  if (e.key === 'PageDown') {
    e.preventDefault();
    if (!state) return;
    const next = state.levelIndex + 1;
    if (next < LEVELS_DATA.length) loadLevel(next);
    return;
  }

  const d = keyMap[e.key];
  if (!d) return;
  e.preventDefault();

  if (inputLocked || aiActive) return;

  // 如果按住的方向变了，重置定时器
  if (holdDir !== e.key) {
    clearHold();
    tryMove(d.dx, d.dy);
    holdDir = e.key;
    holdTimer = setTimeout(() => {
      holdTimer = setInterval(() => {
        if (inputLocked || aiActive) {
          clearHold();
          return;
        }
        tryMove(d.dx, d.dy);
      }, HOLD_INTERVAL);
    }, HOLD_DELAY);
  }
});

document.addEventListener('keyup', (e) => {
  if (holdDir === e.key) {
    clearHold();
  }
});

// ---- 查看答案 ----
function stopAI() {
  aiActive = false;
  clearAnimQueue();
  refreshAnswerUI();
}

function startAI() {
  if (!state || state.won) return;
  if (!hasLevelSolution(state.levelIndex)) {
    refreshAnswerUI();
    return;
  }
  // 先重置关卡，再播放答案
  resetLevel();
  aiActive = true;
  aiStatus.textContent = '执行答案中...';
  refreshAnswerUI();
  const queue = getAnswerQueue(state.levelIndex);
  if (queue.length === 0) {
    stopAI();
    return;
  }
  startAnimQueue(queue);
  aiStatus.textContent = '执行答案中...（' + queue.length + ' 步）';
}

viewAnswerBtn.addEventListener('click', () => {
  if (aiActive) {
    stopAI();
  } else {
    startAI();
  }
});

// ---- UI 更新 ----
function updateUI() {
  if (state) {
    moveCountEl.textContent = '步数：' + state.moves;
  }
  refreshAnswerUI();
}

// ---- 事件绑定 ----
levelSelect.addEventListener('change', () => {
  const idx = parseInt(levelSelect.value, 10);
  loadLevel(idx);
});

undoBtn.addEventListener('click', undo);
resetBtn.addEventListener('click', resetLevel);

// ---- 快捷键弹窗 ----
const shortcutOverlay = document.getElementById('shortcutOverlay');
const shortcutBtn = document.getElementById('shortcutBtn');
const shortcutCloseBtn = document.getElementById('shortcutCloseBtn');

shortcutBtn.addEventListener('click', () => {
  shortcutOverlay.classList.remove('hidden');
});
shortcutCloseBtn.addEventListener('click', () => {
  shortcutOverlay.classList.add('hidden');
});
shortcutOverlay.addEventListener('click', (e) => {
  if (e.target === shortcutOverlay) {
    shortcutOverlay.classList.add('hidden');
  }
});

nextLevelBtn.addEventListener('click', () => {
  if (!state) return;
  const next = state.levelIndex + 1;
  if (next < LEVELS_DATA.length) {
    loadLevel(next);
  } else {
    winOverlay.classList.add('hidden');
  }
});

// ---- 初始化 ----
populateLevelSelect();
const lastLevel = getLastLevel();
loadLevel(lastLevel);
