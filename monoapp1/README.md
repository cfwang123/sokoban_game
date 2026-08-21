# monoapp1 — Mono Sokoban (teaching)

> [中文版](README.ZH.md)

Teaching terminal Sokoban port (`monoapp1/`).

## Level

```bash
# Mono
mcs -out:sokoban.exe Program.cs Game.cs
mono sokoban.exe

# Microsoft csc
# csc /out:sokoban.exe Program.cs Game.cs
# sokoban.exe
```

Controls: WASD move, z undo, r reset, q quit.
