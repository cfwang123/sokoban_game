# flutterapp1 — Flutter 推箱子（教学）

> [English](readme.md)


Dart / Flutter 跨端演示：`CustomPainter` 棋盘 + 点击寻路 + 虚拟方向键。

**版本 1.0.0** · 本仓库不强制 `flutter run` 通过（需本机 Flutter SDK）。

## 结构

```
flutterapp1/
  pubspec.yaml
  lib/main.dart
  lib/game/game_state.dart
  lib/game/pathfinding.dart
  lib/game/mini_levels.dart
```

## 运行（可选）

```bash
cd flutterapp1
flutter pub get
flutter run
```

## 对照

| Flutter | Android 原版 |
|---------|----------------|
| `StatefulWidget` | `MainActivity` |
| `CustomPainter` | `GameBoardView` |
| `shared_preferences`（可接） | SharedPreferences |
