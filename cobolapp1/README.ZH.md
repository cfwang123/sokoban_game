# cobolapp1 — COBOL 推箱子（教学）

> [English](readme.md)


需要 [GnuCOBOL](https://gnucobol.sourceforge.io/)（`cobc`）。

```bash
cd cobolapp1
cobc -x -free main.cbl game.cbl -o sokoban
./sokoban
# Windows:
# sokoban.exe
```

键位：WASD 移动，z 撤销，r 重置，q 退出。

关卡以二维字符地图表示，符合 COBOL 传统数据布局风格。
