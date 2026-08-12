# gtkapp1 — GTK3 Sokoban (teaching)

> [中文版](readme.zh.md)

Teaching terminal Sokoban port (`gtkapp1/`).

## Run

```bash
sudo apt install libgtk-3-dev
cd gtkapp1
gcc -O2 main.c game.c -o sokoban `pkg-config --cflags --libs gtk+-3.0`
./sokoban
```

Controls: WASD move, z undo, r reset, q quit.

## Files

| File | Description |
|------|-------------|
| `game.h` / `game.c` | see Chinese doc |
| `main.c` | `GtkWindow` + `GtkDrawingArea` + Cairo |
| `readme.md` | this document (English) |
| `readme.zh.md` | Chinese document |

## See also

X11   [`../x11app1`](../x11app1) · Win32 [`../win32app1`](../win32app1)
