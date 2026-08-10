// 与 web 教学版同逻辑
(function (global) {
  'use strict';
  var LEVEL = [
    '#######', '#. . .#', '# $$$ #', '#.$@$.#',
    '# $$$ #', '#. . .#', '#######',
  ];
  function key(x, y) { return x + ',' + y; }
  function fromRows(rows) {
    var walls = {}, goals = {}, boxes = {};
    var px = 0, py = 0, maxX = 0, maxY = 0;
    for (var y = 0; y < rows.length; y++) {
      maxY = y;
      for (var x = 0; x < rows[y].length; x++) {
        if (x > maxX) maxX = x;
        var ch = rows[y].charAt(x), k = key(x, y);
        if (ch === '#') walls[k] = true;
        else if (ch === '.') goals[k] = true;
        else if (ch === '$') boxes[k] = true;
        else if (ch === '*') { boxes[k] = true; goals[k] = true; }
        else if (ch === '@') { px = x; py = y; }
        else if (ch === '+') { px = x; py = y; goals[k] = true; }
      }
    }
    return { walls: walls, goals: goals, boxes: boxes, px: px, py: py,
      moves: 0, won: false, width: maxX + 1, height: maxY + 1, hist: [] };
  }
  function checkWin(s) {
    for (var b in s.boxes) {
      if (s.boxes.hasOwnProperty(b) && !s.goals[b]) { s.won = false; return; }
    }
    s.won = true;
  }
  function tryMove(s, dx, dy) {
    if (s.won) return false;
    var nx = s.px + dx, ny = s.py + dy, nk = key(nx, ny);
    if (s.walls[nk]) return false;
    if (s.boxes[nk]) {
      var bx = nx + dx, by = ny + dy, bk = key(bx, by);
      if (s.walls[bk] || s.boxes[bk]) return false;
      s.hist.push({ px: s.px, py: s.py, bf: nk, bt: bk });
      delete s.boxes[nk]; s.boxes[bk] = true;
      s.px = nx; s.py = ny; s.moves++; checkWin(s); return true;
    }
    s.hist.push({ px: s.px, py: s.py, bf: null, bt: null });
    s.px = nx; s.py = ny; return true;
  }
  function undo(s) {
    if (s.won || !s.hist.length) return false;
    while (s.hist.length) {
      var e = s.hist.pop();
      if (e.bf != null) {
        s.px = e.px; s.py = e.py;
        delete s.boxes[e.bt]; s.boxes[e.bf] = true;
        if (s.moves > 0) s.moves--; s.won = false; return true;
      }
      s.px = e.px; s.py = e.py;
    }
    return true;
  }
  global.SokobanCore = {
    key: key,
    newGame: function () { return fromRows(LEVEL); },
    tryMove: tryMove,
    undo: undo,
  };
})(typeof window !== 'undefined' ? window : globalThis);
