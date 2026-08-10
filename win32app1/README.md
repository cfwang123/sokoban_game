# win32app1 — Win32 API 推箱子（教学）

纯 **User32 + GDI** 窗口程序教学源码，**不要求在本仓库内编译**。

## 文件

| 文件 | 说明 |
|------|------|
| `game.h` / `game.c` | 玩法核心 |
| `main.c` | `WinMain` + `WndProc` 绘制与按键 |

## 可选本机编译

```bat
gcc -O2 main.c game.c -o sokoban.exe -mwindows -lgdi32 -luser32
```

或 Visual Studio 开发者命令行：

```bat
cl /O2 main.c game.c user32.lib gdi32.lib /Fe:sokoban.exe
```

## 键位

WASD / 方向键 移动，Z 撤销，R 重置，Esc/Q 退出。

对照：MFC 版 [`../mfcapp1`](../mfcapp1) · Qt 版 [`../qtapp1`](../qtapp1)
