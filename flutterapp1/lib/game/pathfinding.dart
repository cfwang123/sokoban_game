import 'game_state.dart';

/// BFS：避开墙与箱，返回 (dx,dy) 列表。
List<(int, int)>? findPath(GameState s, int tx, int ty) {
  if (s.player.x == tx && s.player.y == ty) return [];
  final blocked = {...s.walls, ...s.boxes};
  final start = s.player.key;
  final target = '$tx,$ty';
  final q = <Pos>[s.player];
  final visited = <String>{start};
  final parent = <String, (String, int, int)>{};
  const dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)];

  while (q.isNotEmpty) {
    final cur = q.removeAt(0);
    final ck = cur.key;
    for (final d in dirs) {
      final nx = cur.x + d.$1;
      final ny = cur.y + d.$2;
      final nk = '$nx,$ny';
      if (blocked.contains(nk) || visited.contains(nk)) continue;
      visited.add(nk);
      parent[nk] = (ck, d.$1, d.$2);
      if (nk == target) {
        final path = <(int, int)>[];
        var p = nk;
        while (p != start) {
          final info = parent[p]!;
          path.insert(0, (info.$2, info.$3));
          p = info.$1;
        }
        return path;
      }
      q.add(Pos(nx, ny));
    }
  }
  return null;
}
