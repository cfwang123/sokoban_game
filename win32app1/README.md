# win32app1 — Win32 API Sokoban (teaching)

> [中文版](README.ZH.md)

Teaching terminal Sokoban port (`win32app1/`).

## Run

```bat
gcc -O2 main.c game.c -o sokoban.exe -mwindows -lgdi32 -luser32
```

```bat
cl /O2 main.c game.c user32.lib gdi32.lib /Fe:sokoban.exe
```

Controls: WASD move, z undo, r reset, q quit.

## Files

| File | Description |
|------|-------------|
| `game.h` / `game.c` | see Chinese doc |
| `main.c` | `WinMain` + `WndProc` |
| `README.md` | this document (English) |
| `README.ZH.md` | Chinese document |

## See also

MFC   [`../mfcapp1`](../mfcapp1) · Qt   [`../qtapp1`](../qtapp1)
