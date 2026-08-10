// Readable Node CLI source — encoded to pure JSFuck by generate.js / main.py --rebuild.
// No require() — only globals (console, process) so JSFuck eval works in Node.
var L = [
  "#######",
  "#. . .#",
  "# $$$ #",
  "#.$@$.#",
  "# $$$ #",
  "#. . .#",
  "#######",
];
function K(x, y) {
  return x + "," + y;
}
function load() {
  var W = {},
    G = {},
    B = {},
    px = 0,
    py = 0,
    w = 0,
    h = 0;
  for (var y = 0; y < L.length; y++) {
    h = y + 1;
    var row = L[y];
    for (var x = 0; x < row.length; x++) {
      w = Math.max(w, x + 1);
      var c = row[x],
        k = K(x, y);
      if (c === "#") W[k] = 1;
      else if (c === ".") G[k] = 1;
      else if (c === "$") B[k] = 1;
      else if (c === "*") {
        B[k] = 1;
        G[k] = 1;
      } else if (c === "@") {
        px = x;
        py = y;
      } else if (c === "+") {
        px = x;
        py = y;
        G[k] = 1;
      }
    }
  }
  return { W: W, G: G, B: B, px: px, py: py, m: 0, won: false, w: w, h: h, hist: [] };
}
function win(s) {
  for (var b in s.B) if (!s.G[b]) {
    s.won = false;
    return;
  }
  s.won = true;
}
function move(s, dx, dy) {
  if (s.won) return;
  var nx = s.px + dx,
    ny = s.py + dy,
    nk = K(nx, ny);
  if (s.W[nk]) return;
  if (s.B[nk]) {
    var bx = nx + dx,
      by = ny + dy,
      bk = K(bx, by);
    if (s.W[bk] || s.B[bk]) return;
    s.hist.push([s.px, s.py, nk, bk]);
    delete s.B[nk];
    s.B[bk] = 1;
    s.px = nx;
    s.py = ny;
    s.m++;
    win(s);
    return;
  }
  s.hist.push([s.px, s.py, null, null]);
  s.px = nx;
  s.py = ny;
}
function undo(s) {
  if (s.won || !s.hist.length) return;
  while (s.hist.length) {
    var e = s.hist.pop(),
      hx = e[0],
      hy = e[1],
      bf = e[2],
      bt = e[3];
    if (bf != null) {
      s.px = hx;
      s.py = hy;
      delete s.B[bt];
      s.B[bf] = 1;
      if (s.m > 0) s.m--;
      s.won = false;
      return;
    }
    s.px = hx;
    s.py = hy;
  }
}
function draw(s) {
  var o = "";
  for (var y = 0; y < s.h; y++) {
    for (var x = 0; x < s.w; x++) {
      var k = K(x, y);
      if (s.px === x && s.py === y) o += s.G[k] ? "+" : "@";
      else if (s.B[k]) o += s.G[k] ? "*" : "$";
      else if (s.W[k]) o += "#";
      else if (s.G[k]) o += ".";
      else o += " ";
    }
    o += "\n";
  }
  return o;
}
var s = load();
console.log("sokoban_jsfuck — wasd z r q");
console.log("(pure JSFuck program; only []()!+)");
function paint() {
  process.stdout.write(
    "\n" + draw(s) + "moves=" + s.m + (s.won ? " WIN!" : "") + "\n> "
  );
}
var buf = "";
function onLine(line) {
  if (!line) {
    paint();
    return;
  }
  var ch = line[0].toLowerCase();
  if (ch === "q") {
    process.stdout.write("bye\n");
    if (process.stdin.pause) process.stdin.pause();
    return;
  }
  if (ch === "r") {
    s = load();
    paint();
    return;
  }
  if (ch === "z") {
    undo(s);
    paint();
    return;
  }
  var M = { w: [0, -1], s: [0, 1], a: [-1, 0], d: [1, 0] };
  if (M[ch] && !s.won) {
    move(s, M[ch][0], M[ch][1]);
    if (s.won) console.log("Level clear!");
  }
  paint();
}
process.stdin.setEncoding("utf8");
process.stdin.on("data", function (chunk) {
  buf += chunk;
  var i;
  while ((i = buf.indexOf("\n")) >= 0) {
    var line = buf.slice(0, i);
    if (line.length && line.charAt(line.length - 1) === "\r")
      line = line.slice(0, -1);
    buf = buf.slice(i + 1);
    onLine(line);
  }
});
if (process.stdin.resume) process.stdin.resume();
paint();
