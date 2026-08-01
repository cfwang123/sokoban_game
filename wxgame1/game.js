/**
 * 微信小游戏入口（教学）。
 * 真机：用微信开发者工具打开本目录，appid 用测试号。
 * 逻辑在 js/game.js；关卡 js/levels_mini.js。
 */
const { parseLevel, tryMove, undo, findPath } = require('./js/game.js');
const { MINI_LEVELS } = require('./js/levels_mini.js');

const sys = wx.getSystemInfoSync();
const canvas = wx.createCanvas();
const ctx = canvas.getContext('2d');
canvas.width = sys.windowWidth;
canvas.height = sys.windowHeight;

let level = 0;
let state = null;

function load(i) {
  level = Math.max(0, Math.min(MINI_LEVELS.length - 1, i));
  state = parseLevel(MINI_LEVELS[level].puzzle, level);
  draw();
}

function draw() {
  const w = canvas.width, h = canvas.height;
  ctx.fillStyle = '#1a1a2e';
  ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#eee';
  ctx.font = '14px sans-serif';
  ctx.fillText('LV' + (level + 1) + '/' + MINI_LEVELS.length + ' 步' + state.moves + (state.won ? ' 过关' : ''), 8, 20);

  const pad = 24, top = 36, bot = 100;
  const cell = Math.floor(Math.min((w - pad * 2) / state.width, (h - top - bot) / state.height));
  const ox = Math.floor((w - cell * state.width) / 2);
  const oy = top + Math.floor((h - top - bot - cell * state.height) / 2);

  for (let y = 0; y < state.height; y++) {
    for (let x = 0; x < state.width; x++) {
      const k = x + ',' + y;
      const px = ox + x * cell, py = oy + y * cell;
      ctx.fillStyle = state.walls.has(k) ? '#4a4a6a' : '#3a3a55';
      ctx.fillRect(px, py, cell - 1, cell - 1);
      if (state.goals.has(k)) {
        ctx.fillStyle = '#e94560';
        ctx.beginPath();
        ctx.arc(px + cell / 2, py + cell / 2, cell * 0.12, 0, Math.PI * 2);
        ctx.fill();
      }
      if (state.boxes.has(k)) {
        ctx.fillStyle = state.goals.has(k) ? '#2ecc71' : '#f39c12';
        ctx.fillRect(px + 3, py + 3, cell - 7, cell - 7);
      }
    }
  }
  ctx.fillStyle = '#3498db';
  ctx.beginPath();
  ctx.arc(ox + state.player.x * cell + cell / 2, oy + state.player.y * cell + cell / 2, cell * 0.32, 0, Math.PI * 2);
  ctx.fill();

  // 虚拟键区域
  drawBtn(w / 2 - 24, h - 90, '↑');
  drawBtn(w / 2 - 80, h - 50, '←');
  drawBtn(w / 2 - 24, h - 50, '↓');
  drawBtn(w / 2 + 32, h - 50, '→');
  drawBtn(16, h - 50, '撤');
  drawBtn(w - 56, h - 50, '下');
}

function drawBtn(x, y, t) {
  ctx.fillStyle = '#0f3460';
  ctx.fillRect(x, y, 48, 36);
  ctx.fillStyle = '#eee';
  ctx.fillText(t, x + 14, y + 24);
}

function hitBtn(tx, ty, x, y) {
  return tx >= x && tx < x + 48 && ty >= y && ty < y + 36;
}

wx.onTouchEnd((e) => {
  const t = e.changedTouches[0];
  const x = t.clientX, y = t.clientY;
  const w = canvas.width, h = canvas.height;
  if (hitBtn(x, y, w / 2 - 24, h - 90)) tryMove(state, 0, -1);
  else if (hitBtn(x, y, w / 2 - 24, h - 50)) tryMove(state, 0, 1);
  else if (hitBtn(x, y, w / 2 - 80, h - 50)) tryMove(state, -1, 0);
  else if (hitBtn(x, y, w / 2 + 32, h - 50)) tryMove(state, 1, 0);
  else if (hitBtn(x, y, 16, h - 50)) undo(state);
  else if (hitBtn(x, y, w - 56, h - 50)) load(level + 1);
  else {
    // 棋盘点击寻路
    const pad = 24, top = 36, bot = 100;
    const cell = Math.floor(Math.min((w - pad * 2) / state.width, (h - top - bot) / state.height));
    const ox = Math.floor((w - cell * state.width) / 2);
    const oy = top + Math.floor((h - top - bot - cell * state.height) / 2);
    const gx = Math.floor((x - ox) / cell), gy = Math.floor((y - oy) / cell);
    if (gx >= 0 && gy >= 0 && gx < state.width && gy < state.height) {
      const k = gx + ',' + gy;
      if (state.boxes.has(k)) {
        const dx = gx - state.player.x, dy = gy - state.player.y;
        if (Math.abs(dx) + Math.abs(dy) === 1) tryMove(state, dx, dy);
      } else if (!state.walls.has(k) && !state.boxes.has(k)) {
        const path = findPath(state, gx, gy);
        if (path) for (const [dx, dy] of path) { tryMove(state, dx, dy); if (state.won) break; }
      }
    }
  }
  draw();
});

load(0);
