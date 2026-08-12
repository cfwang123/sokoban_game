# gtkapp1 — GTK3 推箱子（教学）

> [English](readme.md)


**GTK** 桌面教学源码（用户消息中的 “gtx” 按 **GTK** 理解），**不要求在本仓库内编译**。

## 文件

| 文件 | 说明 |
|------|------|
| `game.h` / `game.c` | 玩法核心 |
| `main.c` | `GtkWindow` + `GtkDrawingArea` + Cairo |

## 可选本机编译（Linux）

```bash
sudo apt install libgtk-3-dev
cd gtkapp1
gcc -O2 main.c game.c -o sokoban `pkg-config --cflags --libs gtk+-3.0`
./sokoban
```

键位：WASD / 方向键，Z 撤销，R 重置，Q/Esc 退出。

对照：X11 裸协议 [`../x11app1`](../x11app1) · Win32 [`../win32app1`](../win32app1)
