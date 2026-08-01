// 浏览器扩展共用推箱子逻辑（Chrome / Edge / Firefox 拷贝同一份）
(function (global) {
  "use strict";

  var LEVELS = [
    { name: "1 L", puzzle: ["###", "#@#", "#$#", "#.#", "###"] },
    { name: "1 R", puzzle: ["#####", "#.$@#", "#####"] },
    { name: "2 L", puzzle: ["###", "#.###", "#*$-#", "#--@#", "#####"] },
    {
      name: "Star",
      puzzle: [
        "#######",
        "#. . .#",
        "# $$$ #",
        "#.$@$.#",
        "# $$$ #",
        "#. . .#",
        "#######",
      ],
    },
  ];

  function parse(rows, index) {
    var walls = {},
      goals = {},
      boxes = {},
      player = { x: 0, y: 0 },
      maxX = 0,
      maxY = 0;
    for (var y = 0; y < rows.length; y++) {
      maxY = y;
      var row = rows[y];
      for (var x = 0; x < row.length; x++) {
        if (x > maxX) maxX = x;
        var k = x + "," + y,
          ch = row.charAt(x);
        if (ch === "#") walls[k] = 1;
        else if (ch === ".") goals[k] = 1;
        else if (ch === "$") boxes[k] = 1;
        else if (ch === "*") {
          boxes[k] = 1;
          goals[k] = 1;
        } else if (ch === "@") player = { x: x, y: y };
        else if (ch === "+") {
          player = { x: x, y: y };
          goals[k] = 1;
        }
      }
    }
    return {
      walls: walls,
      goals: goals,
      boxes: boxes,
      player: player,
      moves: 0,
      won: false,
      history: [],
      w: maxX + 1,
      h: maxY + 1,
      index: index,
    };
  }

  function tryMove(s, dx, dy) {
    if (s.won) return false;
    var nx = s.player.x + dx,
      ny = s.player.y + dy,
      nk = nx + "," + ny;
    if (s.walls[nk]) return false;
    if (s.boxes[nk]) {
      var bk = nx + dx + "," + (ny + dy);
      if (s.walls[bk] || s.boxes[bk]) return false;
      s.history.push({
        px: s.player.x,
        py: s.player.y,
        from: nk,
        to: bk,
        push: true,
      });
      delete s.boxes[nk];
      s.boxes[bk] = 1;
      s.player = { x: nx, y: ny };
      s.moves++;
      s.won = true;
      for (var b in s.boxes) {
        if (s.boxes.hasOwnProperty(b) && !s.goals[b]) {
          s.won = false;
          break;
        }
      }
      return true;
    }
    s.history.push({ px: s.player.x, py: s.player.y, push: false });
    s.player = { x: nx, y: ny };
    return true;
  }

  function undo(s) {
    if (s.won || !s.history.length) return;
    var e;
    while (s.history.length) {
      e = s.history.pop();
      if (e.push) break;
      s.player = { x: e.px, y: e.py };
    }
    if (!e || !e.push) return;
    s.player = { x: e.px, y: e.py };
    delete s.boxes[e.to];
    s.boxes[e.from] = 1;
    if (s.moves > 0) s.moves--;
    s.won = false;
  }

  function findPath(s, tx, ty) {
    var start = s.player.x + "," + s.player.y,
      target = tx + "," + ty;
    if (start === target) return [];
    var blocked = {};
    for (var k in s.walls) if (s.walls[k]) blocked[k] = 1;
    for (k in s.boxes) if (s.boxes[k]) blocked[k] = 1;
    var q = [{ x: s.player.x, y: s.player.y }],
      qi = 0,
      vis = {},
      parent = {};
    vis[start] = 1;
    var dirs = [
      [0, -1],
      [0, 1],
      [-1, 0],
      [1, 0],
    ];
    while (qi < q.length) {
      var c = q[qi++];
      var ck = c.x + "," + c.y;
      for (var di = 0; di < 4; di++) {
        var nx = c.x + dirs[di][0],
          ny = c.y + dirs[di][1],
          nk = nx + "," + ny;
        if (blocked[nk] || vis[nk]) continue;
        vis[nk] = 1;
        parent[nk] = { from: ck, dx: dirs[di][0], dy: dirs[di][1] };
        if (nk === target) {
          var path = [],
            p = nk;
          while (p !== start) {
            var info = parent[p];
            path.unshift([info.dx, info.dy]);
            p = info.from;
          }
          return path;
        }
        q.push({ x: nx, y: ny });
      }
    }
    return null;
  }

  global.SokobanGame = {
    LEVELS: LEVELS,
    parse: parse,
    tryMove: tryMove,
    undo: undo,
    findPath: findPath,
  };
})(typeof window !== "undefined" ? window : this);
