import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'game/game_state.dart';
import 'game/mini_levels.dart';
import 'game/pathfinding.dart';

void main() => runApp(const SokobanApp());

class SokobanApp extends StatelessWidget {
  const SokobanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '推箱子 Flutter',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        colorSchemeSeed: const Color(0xFFE94560),
        useMaterial3: true,
      ),
      home: const GamePage(),
    );
  }
}

class GamePage extends StatefulWidget {
  const GamePage({super.key});
  @override
  State<GamePage> createState() => _GamePageState();
}

class _GamePageState extends State<GamePage> {
  late GameState state;
  int level = 0;
  String status = '';

  @override
  void initState() {
    super.initState();
    _load(0);
  }

  void _load(int i) {
    level = i.clamp(0, miniLevels.length - 1);
    final lv = miniLevels[level];
    state = GameState.fromPuzzle(
      List<String>.from(lv['puzzle'] as List),
      level,
    );
    status = (lv['solution'] as String).isNotEmpty ? '有答案' : '暂无答案';
    setState(() {});
  }

  void _move(int dx, int dy) {
    if (state.won) return;
    if (state.tryMove(dx, dy)) setState(() {});
  }

  void _onTapCell(int gx, int gy) {
    if (state.won) return;
    final key = '$gx,$gy';
    if (state.boxes.contains(key)) {
      final dx = gx - state.player.x;
      final dy = gy - state.player.y;
      if (dx.abs() + dy.abs() == 1) _move(dx, dy);
      return;
    }
    if (state.walls.contains(key) || state.boxes.contains(key)) return;
    final path = findPath(state, gx, gy);
    if (path == null || path.isEmpty) return;
    for (final d in path) {
      state.tryMove(d.$1, d.$2);
      if (state.won) break;
    }
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A2E),
      appBar: AppBar(
        title: Text('LV${level + 1}/${miniLevels.length} · 步${state.moves}'),
        actions: [
          IconButton(icon: const Icon(Icons.undo), onPressed: () {
            state.undo();
            setState(() {});
          }),
          IconButton(icon: const Icon(Icons.refresh), onPressed: () => _load(level)),
          IconButton(
            icon: const Icon(Icons.chevron_left),
            onPressed: level > 0 ? () => _load(level - 1) : null,
          ),
          IconButton(
            icon: const Icon(Icons.chevron_right),
            onPressed: level + 1 < miniLevels.length ? () => _load(level + 1) : null,
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8),
            child: Text(status, style: const TextStyle(color: Colors.white54)),
          ),
          Expanded(
            child: LayoutBuilder(
              builder: (context, c) {
                return GestureDetector(
                  onTapUp: (d) {
                    final cell = _cellSize(c.biggest);
                    final ox = (c.maxWidth - cell * state.width) / 2;
                    final oy = (c.maxHeight - cell * state.height) / 2;
                    final gx = ((d.localPosition.dx - ox) / cell).floor();
                    final gy = ((d.localPosition.dy - oy) / cell).floor();
                    if (gx >= 0 && gy >= 0 && gx < state.width && gy < state.height) {
                      _onTapCell(gx, gy);
                    }
                  },
                  child: CustomPaint(
                    painter: BoardPainter(state),
                    size: Size.infinite,
                  ),
                );
              },
            ),
          ),
          if (state.won)
            const Padding(
              padding: EdgeInsets.all(12),
              child: Text('过关！→ 下一关', style: TextStyle(color: Color(0xFFE94560), fontSize: 18)),
            ),
          _pad(),
          const SizedBox(height: 12),
        ],
      ),
    );
  }

  double _cellSize(Size size) {
    final cw = size.width / state.width;
    final ch = size.height / state.height;
    return cw < ch ? cw : ch;
  }

  Widget _pad() {
    Widget b(IconData i, VoidCallback f) => IconButton.filledTonal(
          onPressed: f,
          icon: Icon(i),
        );
    return Column(
      children: [
        b(Icons.keyboard_arrow_up, () => _move(0, -1)),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            b(Icons.keyboard_arrow_left, () => _move(-1, 0)),
            b(Icons.keyboard_arrow_down, () => _move(0, 1)),
            b(Icons.keyboard_arrow_right, () => _move(1, 0)),
          ],
        ),
      ],
    );
  }
}

class BoardPainter extends CustomPainter {
  final GameState state;
  BoardPainter(this.state);

  @override
  void paint(Canvas canvas, Size size) {
    final cell = (size.width / state.width < size.height / state.height)
        ? size.width / state.width
        : size.height / state.height;
    final ox = (size.width - cell * state.width) / 2;
    final oy = (size.height - cell * state.height) / 2;

    final floor = Paint()..color = const Color(0xFF3A3A55);
    final wall = Paint()..color = const Color(0xFF4A4A6A);
    final goal = Paint()..color = const Color(0xFFE94560);
    final box = Paint()..color = const Color(0xFFF39C12);
    final boxOk = Paint()..color = const Color(0xFF2ECC71);
    final player = Paint()..color = const Color(0xFF3498DB);

    for (var y = 0; y < state.height; y++) {
      for (var x = 0; x < state.width; x++) {
        final r = Rect.fromLTWH(ox + x * cell, oy + y * cell, cell, cell);
        final k = '$x,$y';
        if (state.walls.contains(k)) {
          canvas.drawRect(r, wall);
        } else {
          canvas.drawRect(r, floor);
        }
        if (state.goals.contains(k)) {
          canvas.drawCircle(r.center, cell * 0.12, goal);
        }
        if (state.boxes.contains(k)) {
          final inset = r.deflate(cell * 0.1);
          canvas.drawRRect(
            RRect.fromRectAndRadius(inset, const Radius.circular(4)),
            state.goals.contains(k) ? boxOk : box,
          );
        }
      }
    }
    final pr = Rect.fromLTWH(
      ox + state.player.x * cell,
      oy + state.player.y * cell,
      cell,
      cell,
    );
    canvas.drawCircle(pr.center, cell * 0.35, player);
  }

  @override
  bool shouldRepaint(covariant BoardPainter old) => true;
}
