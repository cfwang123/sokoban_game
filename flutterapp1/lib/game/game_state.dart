/// 推箱子状态（对齐 html_app：纯移动不计步，撤销只撤推箱）。
class Pos {
  final int x;
  final int y;
  const Pos(this.x, this.y);
  Pos offset(int dx, int dy) => Pos(x + dx, y + dy);
  String get key => '$x,$y';
}

class GameState {
  final Set<String> walls;
  final Set<String> goals;
  final Set<String> boxes;
  Pos player;
  final int levelIndex;
  final int width;
  final int height;
  int moves = 0;
  bool won = false;
  final List<_Hist> _hist = [];

  GameState({
    required this.walls,
    required this.goals,
    required this.boxes,
    required this.player,
    required this.levelIndex,
    required this.width,
    required this.height,
  });

  bool isWall(Pos p) => walls.contains(p.key);
  bool isBox(Pos p) => boxes.contains(p.key);
  bool isGoal(Pos p) => goals.contains(p.key);

  bool tryMove(int dx, int dy) {
    if (won) return false;
    final next = player.offset(dx, dy);
    if (isWall(next)) return false;
    if (isBox(next)) {
      final boxNext = next.offset(dx, dy);
      if (isWall(boxNext) || isBox(boxNext)) return false;
      _hist.add(_Hist(player, next, boxNext));
      boxes.remove(next.key);
      boxes.add(boxNext.key);
      player = next;
      moves++;
      _checkWin();
      return true;
    }
    _hist.add(_Hist(player, null, null));
    player = next;
    return true;
  }

  bool undo() {
    if (won || _hist.isEmpty) return false;
    _Hist? e;
    while (_hist.isNotEmpty) {
      e = _hist.removeLast();
      if (e.boxFrom != null) break;
      player = e.player;
    }
    if (e == null || e.boxFrom == null || e.boxTo == null) return true;
    player = e.player;
    boxes.remove(e.boxTo!.key);
    boxes.add(e.boxFrom!.key);
    if (moves > 0) moves--;
    won = false;
    return true;
  }

  void _checkWin() {
    for (final b in boxes) {
      if (!goals.contains(b)) {
        won = false;
        return;
      }
    }
    won = true;
  }

  static GameState fromPuzzle(List<String> rows, int index) {
    final walls = <String>{};
    final goals = <String>{};
    final boxes = <String>{};
    Pos player = const Pos(0, 0);
    var maxX = 0;
    var maxY = 0;
    for (var y = 0; y < rows.length; y++) {
      final row = rows[y];
      maxY = y;
      for (var x = 0; x < row.length; x++) {
        if (x > maxX) maxX = x;
        final ch = row[x];
        final k = '$x,$y';
        switch (ch) {
          case '#':
            walls.add(k);
            break;
          case '.':
            goals.add(k);
            break;
          case r'$':
            boxes.add(k);
            break;
          case '*':
            boxes.add(k);
            goals.add(k);
            break;
          case '@':
            player = Pos(x, y);
            break;
          case '+':
            player = Pos(x, y);
            goals.add(k);
            break;
        }
      }
    }
    return GameState(
      walls: walls,
      goals: goals,
      boxes: boxes,
      player: player,
      levelIndex: index,
      width: maxX + 1,
      height: maxY + 1,
    );
  }
}

class _Hist {
  final Pos player;
  final Pos? boxFrom;
  final Pos? boxTo;
  _Hist(this.player, this.boxFrom, this.boxTo);
}
