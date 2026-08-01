(function () {
  "use strict";
  var G = window.SokobanGame;
  var level = 0;
  var state = null;
  var canvas = document.getElementById("board");
  var ctx = canvas.getContext("2d");
  var info = document.getElementById("info");

  // Safari / Firefox / Chrome 存储兼容
  var storageApi =
    (typeof browser !== "undefined" && browser.storage && browser.storage.local) ||
    (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) ||
    null;

  function storageGet(keys, cb) {
    if (!storageApi) {
      cb({});
      return;
    }
    var p = storageApi.get(keys);
    if (p && typeof p.then === "function") {
      p.then(cb).catch(function () {
        cb({});
      });
    } else {
      storageApi.get(keys, cb);
    }
  }

  function storageSet(obj) {
    if (!storageApi) return;
    var p = storageApi.set(obj);
    if (p && typeof p.then === "function") {
      p.catch(function () {});
    }
  }

  function load(i, save) {
    level = Math.max(0, Math.min(G.LEVELS.length - 1, i));
    state = G.parse(G.LEVELS[level].puzzle, level);
    if (save !== false) storageSet({ sokoban_level: level });
    draw();
  }

  function draw() {
    var s = state;
    var pad = 8;
    var cell = Math.floor(
      Math.min((canvas.width - pad * 2) / s.w, (canvas.height - pad * 2) / s.h)
    );
    var ox = (canvas.width - cell * s.w) / 2;
    var oy = (canvas.height - cell * s.h) / 2;
    ctx.fillStyle = "#2d2d44";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (var y = 0; y < s.h; y++) {
      for (var x = 0; x < s.w; x++) {
        var k = x + "," + y;
        var px = ox + x * cell,
          py = oy + y * cell;
        ctx.fillStyle = s.walls[k] ? "#4a4a6a" : "#3a3a55";
        ctx.fillRect(px, py, cell - 1, cell - 1);
        if (s.goals[k]) {
          ctx.fillStyle = "#e94560";
          ctx.beginPath();
          ctx.arc(px + cell / 2, py + cell / 2, cell * 0.12, 0, Math.PI * 2);
          ctx.fill();
        }
        if (s.boxes[k]) {
          ctx.fillStyle = s.goals[k] ? "#2ecc71" : "#f39c12";
          ctx.fillRect(px + 2, py + 2, cell - 5, cell - 5);
        }
      }
    }
    ctx.fillStyle = "#3498db";
    ctx.beginPath();
    ctx.arc(
      ox + s.player.x * cell + cell / 2,
      oy + s.player.y * cell + cell / 2,
      cell * 0.32,
      0,
      Math.PI * 2
    );
    ctx.fill();
    info.textContent =
      "LV" +
      (level + 1) +
      "/" +
      G.LEVELS.length +
      " · " +
      G.LEVELS[level].name +
      " · 步" +
      s.moves +
      (s.won ? " · 过关" : "");
  }

  function onKey(e) {
    var map = {
      ArrowUp: [0, -1],
      ArrowDown: [0, 1],
      ArrowLeft: [-1, 0],
      ArrowRight: [1, 0],
      w: [0, -1],
      s: [0, 1],
      a: [-1, 0],
      d: [1, 0],
      W: [0, -1],
      S: [0, 1],
      A: [-1, 0],
      D: [1, 0],
    };
    if (e.key === "z" || e.key === "Z") {
      G.undo(state);
      draw();
      e.preventDefault();
      return;
    }
    if (e.key === "r" || e.key === "R") {
      load(level);
      e.preventDefault();
      return;
    }
    var d = map[e.key];
    if (d) {
      G.tryMove(state, d[0], d[1]);
      draw();
      e.preventDefault();
    }
  }

  canvas.addEventListener("click", function (e) {
    var rect = canvas.getBoundingClientRect();
    var mx = e.clientX - rect.left;
    var my = e.clientY - rect.top;
    var pad = 8;
    var cell = Math.floor(
      Math.min((canvas.width - pad * 2) / state.w, (canvas.height - pad * 2) / state.h)
    );
    var ox = (canvas.width - cell * state.w) / 2;
    var oy = (canvas.height - cell * state.h) / 2;
    var gx = Math.floor((mx - ox) / cell);
    var gy = Math.floor((my - oy) / cell);
    if (gx < 0 || gy < 0 || gx >= state.w || gy >= state.h) return;
    var k = gx + "," + gy;
    if (state.boxes[k]) {
      var dx = gx - state.player.x,
        dy = gy - state.player.y;
      if (Math.abs(dx) + Math.abs(dy) === 1) G.tryMove(state, dx, dy);
    } else if (!state.walls[k] && !state.boxes[k]) {
      var path = G.findPath(state, gx, gy);
      if (path) {
        for (var i = 0; i < path.length; i++) {
          G.tryMove(state, path[i][0], path[i][1]);
          if (state.won) break;
        }
      }
    }
    draw();
  });

  document.getElementById("undo").onclick = function () {
    G.undo(state);
    draw();
  };
  document.getElementById("reset").onclick = function () {
    load(level);
  };
  document.getElementById("prev").onclick = function () {
    load(level - 1);
  };
  document.getElementById("next").onclick = function () {
    load(level + 1);
  };
  document.addEventListener("keydown", onKey);

  storageGet(["sokoban_level"], function (r) {
    var n = r && typeof r.sokoban_level === "number" ? r.sokoban_level : 0;
    load(n, false);
  });
})();
