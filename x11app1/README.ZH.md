# x11app1 — X11 / Xlib 推箱子（教学）

> [English](readme.md)


Linux/Unix **X11 原生窗口**教学源码，**不要求在本仓库内编译**。

## 文件

| 文件 | 说明 |
|------|------|
| `game.h` / `game.c` | 玩法核心 |
| `main.c` | XOpenDisplay / 事件循环 / 绘制 |

## 可选本机编译（Linux + libX11）

```bash
sudo apt install libx11-dev   # Debian/Ubuntu 示例
cd x11app1
gcc -O2 main.c game.c -o sokoban -lX11
./sokoban
```

键位：WASD / 方向键，Z 撤销，R 重置，Q/Esc 退出。

对照：Win32 [`../win32app1`](../win32app1) · GTK [`../gtkapp1`](../gtkapp1)
