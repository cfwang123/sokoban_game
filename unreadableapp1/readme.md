# unreadableapp1 — Unreadable Sokoban (full game)

> [中文版](readme.zh.md)

Pure [Unreadable](https://esolangs.org/wiki/Unreadable) mini Sokoban (same policy as `brainfuckapp1` / `befungeapp1`: gameplay in the target language; Python is interpreter only).

Source uses only `'` and `"`; commands are determined by quote counts (PRINT / INC / ONE / DO / WHILE / SET / GET / DEC / IF / IN).

```bash
cd unreadableapp1
python -X utf8 main.py
python -X utf8 main.py --test
# or
python -X utf8 interpreter.py sokoban.unr
```

| Key | Action |
|-----|--------|
| WASD | move / push |
| z | undo |
| r | reset |
| q | quit |

## Files

| File | Description |
|------|-------------|
| `sokoban.unr` | **pure Unreadable** full game (generated) |
| `interpreter.py` | Unreadable interpreter (parse + eval) |
| `main.py` | run / `--test` / `--rebuild` |
| `readme.md` | this document (English) |
| `readme.zh.md` | Chinese document |

Regenerate `sokoban.unr`:

```bash
python -X utf8 main.py --rebuild
# or
python -X utf8 scripts/_gen_unreadable_sokoban.py
```

## Notes

- Dialect matches [esolangs Unreadable](https://esolangs.org/wiki/Unreadable); top-level expressions run in order.
- Map, player, undo history live in the Unreadable variable array (`SET`/`GET`).
- Only `+1`/`-1` arithmetic — rendering/compare are slow by design.
