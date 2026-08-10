// dartapp1 — Dart 推箱子终端版（教学）
// 运行: dart run main.dart

import 'dart:io';
import 'game.dart';

const level = [
  '#######',
  '#. . .#',
  '# $$$ #',
  '#.$@$.#',
  '# $$$ #',
  '#. . .#',
  '#######',
];

void main() {
  var state = GameState.fromRows(level, 0);
  stdout.writeln('sokoban_dart — wasd 移动, z 撤销, r 重置, q 退出');
  while (true) {
    stdout.writeln();
    stdout.write(state.renderAscii());
    final flag = state.won ? ' WIN!' : '';
    stdout.write('moves=${state.moves}$flag\n> ');
    final line = stdin.readLineSync();
    if (line == null) break;
    final t = line.trim();
    if (t.isEmpty) continue;
    final ch = t[0].toLowerCase();
    switch (ch) {
      case 'w':
        state.tryMove(0, -1);
        break;
      case 's':
        state.tryMove(0, 1);
        break;
      case 'a':
        state.tryMove(-1, 0);
        break;
      case 'd':
        state.tryMove(1, 0);
        break;
      case 'z':
        state.undo();
        break;
      case 'r':
        state = GameState.fromRows(level, 0);
        break;
      case 'q':
        return;
    }
    if (state.won) stdout.writeln('Level clear!');
  }
}
