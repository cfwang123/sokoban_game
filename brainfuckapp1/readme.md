# brainfuckapp1 — Brainfuck Sokoban (teaching)

> [中文版](readme.zh.md)

Mini-level terminal port in pure **Brainfuck**. In-repo Python interpreter — no separate `bf` tool required.

```bash
cd brainfuckapp1
python -X utf8 main.py
```

You can also run `sokoban.bf` with any compatible Brainfuck interpreter (non `+-<>[],.` characters are ignored).

Controls: WASD move, z undo, r reset, q quit.

## Files

| File | Description |
|------|-------------|
| `sokoban.bf` | Brainfuck source (generator-expanded; ~1M instructions) |
| `main.py` | small BF interpreter + line-buffered input |
| `readme.md` | this document (English) |
| `readme.zh.md` | Chinese document |

Regenerate `sokoban.bf` (maintenance):

```bash
python -X utf8 scripts/_gen_brainfuck_sokoban.py
```

## Notes

- Same mini level as other `*app1` teaching ports (7×7).
- Undo matches other ports: rewind through the last box push.
- Comment lines must not contain `+ - < > [ ] , .` or they execute as code.
