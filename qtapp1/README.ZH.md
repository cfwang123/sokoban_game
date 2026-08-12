# qtapp1 — Qt 推箱子桌面 demo（教学）

> [English](readme.md)


单文件 `QWidget` + `QPainter`。需要 Qt 5.15+ / Qt 6 与 `qmake` 或 Qt Creator。

```bash
cd qtapp1
qmake qtapp1.pro
make   # 或 nmake / mingw32-make
./sokoban
```

Windows（Qt 安装后）：

```bat
qmake qtapp1.pro
mingw32-make
sokoban.exe
```

键位：WASD / 方向键，Z 撤销，R 重置，Q 退出。

对照：`pygameapp1/`、`sdlapp1/`、`html_app/`。
