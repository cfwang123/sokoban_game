/**
 * cocos2dapp1 — 教学用「类 Cocos2d」场景循环
 * Director / Layer / scheduleUpdate 概念映射到 requestAnimationFrame + 手写 Layer.draw
 * 无需安装 Cocos Creator；逻辑可迁入 cc.Component。
 */
(function () {
  var CELL = 40;
  var PAD = 16;
  var canvas = document.getElementById('c');
  var ctx = canvas.getContext('2d');
  var statusEl = document.getElementById('status');

  // --- 模拟 Director + 当前 Scene ---
  var Director = {
    scene: null,
    runScene: function (scene) {
      this.scene = scene;
      if (scene.onEnter) scene.onEnter();
    },
  };

  // --- Layer：持有游戏状态与绘制 ---
  function GameLayer() {
    this.state = SokobanCore.newGame();
  }
  GameLayer.prototype.onEnter = function () {
    var self = this;
    window.addEventListener('keydown', function (e) {
      var k = e.key.toLowerCase();
      if (k === 'w' || e.key === 'ArrowUp') SokobanCore.tryMove(self.state, 0, -1);
      else if (k === 's' || e.key === 'ArrowDown') SokobanCore.tryMove(self.state, 0, 1);
      else if (k === 'a' || e.key === 'ArrowLeft') SokobanCore.tryMove(self.state, -1, 0);
      else if (k === 'd' || e.key === 'ArrowRight') SokobanCore.tryMove(self.state, 1, 0);
      else if (k === 'z') SokobanCore.undo(self.state);
      else if (k === 'r') self.state = SokobanCore.newGame();
    });
  };
  GameLayer.prototype.update = function (/* dt */) {
    // 教学：可在此做插值动画
  };
  GameLayer.prototype.draw = function () {
    var s = this.state;
    var w = PAD * 2 + s.width * CELL;
    var h = PAD * 2 + s.height * CELL + 24;
    if (canvas.width !== w) canvas.width = w;
    if (canvas.height !== h) canvas.height = h;
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    var x, y, k;
    for (y = 0; y < s.height; y++) {
      for (x = 0; x < s.width; x++) {
        k = SokobanCore.key(x, y);
        var rx = PAD + x * CELL;
        var ry = PAD + y * CELL;
        if (s.walls[k]) {
          ctx.fillStyle = '#4a4a6a';
          ctx.fillRect(rx, ry, CELL, CELL);
        } else {
          ctx.fillStyle = '#3a3a55';
          ctx.fillRect(rx, ry, CELL, CELL);
          ctx.strokeStyle = '#444466';
          ctx.strokeRect(rx + 0.5, ry + 0.5, CELL - 1, CELL - 1);
          if (s.goals[k]) {
            ctx.fillStyle = '#e94560';
            ctx.beginPath();
            ctx.arc(rx + CELL / 2, ry + CELL / 2, 6, 0, Math.PI * 2);
            ctx.fill();
          }
          if (s.boxes[k]) {
            ctx.fillStyle = s.goals[k] ? '#2ecc71' : '#f39c12';
            ctx.fillRect(rx + 4, ry + 4, CELL - 8, CELL - 8);
          }
        }
        if (s.px === x && s.py === y) {
          ctx.fillStyle = '#3498db';
          ctx.beginPath();
          ctx.arc(rx + CELL / 2, ry + CELL / 2, CELL * 0.32, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }
    ctx.fillStyle = '#fff';
    ctx.font = '14px system-ui,sans-serif';
    ctx.fillText(
      'moves=' + s.moves + (s.won ? ' WIN' : '') + '  WASD Z R',
      8,
      PAD + s.height * CELL + 16
    );
    statusEl.textContent = s.won ? 'Level clear!' : 'Cocos-style Layer · scheduleUpdate';
  };

  var layer = new GameLayer();
  Director.runScene(layer);

  var last = performance.now();
  function loop(now) {
    var dt = (now - last) / 1000;
    last = now;
    if (Director.scene) {
      Director.scene.update(dt);
      Director.scene.draw();
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
