// 推箱子核心逻辑（Dart 教学）

class Hist {
  final int px, py;
  final String? boxFrom, boxTo;
  Hist(this.px, this.py, [this.boxFrom, this.boxTo]);
}

class GameState {
  final Set<String> walls = {};
  final Set<String> goals = {};
  final Set<String> boxes = {};
  int px = 0, py = 0;
  int moves = 0;
  bool won = false;
  int width = 0, height = 0;
  final List<Hist> hist = [];

  static String key(int x, int y) => '$x,$y';

  static GameState fromRows(List<String> rows, [int index = 0]) {
    final s = GameState();
    var maxX = 0, maxY = 0;
    for (var y = 0; y < rows.length; y++) {
      maxY = y;
      final row = rows[y];
      for (var x = 0; x < row.length; x++) {
        if (x > maxX) maxX = x;
        final ch = row[x];
        final k = key(x, y);
        switch (ch) {
          case '#':
            s.walls.add(k);
            break;
          case '.':
            s.goals.add(k);
            break;
          case r'$':
            s.boxes.add(k);
            break;
          case '*':
            s.boxes.add(k);
            s.goals.add(k);
            break;
          case '@':
            s.px = x;
            s.py = y;
            break;
          case '+':
            s.px = x;
            s.py = y;
            s.goals.add(k);
            break;
        }
      }
    }
    s.width = maxX + 1;
    s.height = maxY + 1;
    return s;
  }

  void checkWin() {
    won = boxes.every((b) => goals.contains(b));
  }

  bool tryMove(int dx, int dy) {
    if (won) return false;
    final nx = px + dx, ny = py + dy;
    final nk = key(nx, ny);
    if (walls.contains(nk)) return false;
    if (boxes.contains(nk)) {
      final bx = nx + dx, by = ny + dy;
      final bk = key(bx, by);
      if (walls.contains(bk) || boxes.contains(bk)) return false;
      hist.add(Hist(px, py, nk, bk));
      boxes.remove(nk);
      boxes.add(bk);
      px = nx;
      py = ny;
      moves++;
      checkWin();
      return true;
    }
    hist.add(Hist(px, py));
    px = nx;
    py = ny;
    return true;
  }

  bool undo() {
    if (won || hist.isEmpty) return false;
    Hist? entry;
    while (hist.isNotEmpty) {
      entry = hist.removeLast();
      if (entry.boxFrom != null) break;
      px = entry.px;
      py = entry.py;
    }
    if (entry == null || entry.boxFrom == null) return true;
    px = entry.px;
    py = entry.py;
    boxes.remove(entry.boxTo);
    boxes.add(entry.boxFrom!);
    if (moves > 0) moves--;
    won = false;
    return true;
  }

  String renderAscii() {
    final sb = StringBuffer();
    for (var y = 0; y < height; y++) {
      for (var x = 0; x < width; x++) {
        final k = key(x, y);
        if (px == x && py == y) {
          sb.write(goals.contains(k) ? '+' : '@');
        } else if (boxes.contains(k)) {
          sb.write(goals.contains(k) ? '*' : r'$');
        } else if (walls.contains(k)) {
          sb.write('#');
        } else if (goals.contains(k)) {
          sb.write('.');
        } else {
          sb.write(' ');
        }
      }
      sb.writeln();
    }
    return sb.toString();
  }
}
