# x11app1 — X11 / Xlib Sokoban (teaching)

> [中文版](README.ZH.md)

Teaching terminal Sokoban port (`x11app1/`).

## Run

```bash
sudo apt install libx11-dev # Debian/Ubuntu
cd x11app1
gcc -O2 main.c game.c -o sokoban -lX11
./sokoban
```

Controls: WASD move, z undo, r reset, q quit.

## Files

| File | Description |
|------|-------------|
| `game.h` / `game.c` | see Chinese doc |
| `main.c` | XOpenDisplay / / |
| `README.md` | this document (English) |
| `README.ZH.md` | Chinese document |

## See also

Win32 [`../win32app1`](../win32app1) · GTK [`../gtkapp1`](../gtkapp1)
