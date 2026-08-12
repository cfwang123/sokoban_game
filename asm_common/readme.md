# asm_common — shared C reference for assembly teaching

> [中文版](readme.zh.md)

Each `asm_*app1` folder implements the same `sk_try_move` semantics in `.s` / `.S` / `.asm` / `.wat`. Compare against this C reference.

| File | Description |
|------|-------------|
| `game.h` / `game.c` | full gameplay (reset / try_move / undo / render) |
| `host_main.c` | terminal loop |
| `test_try_move.c` | `sk_try_move` self-test (C or asm) |
| `readme.md` | this document (English) |
| `readme.zh.md` | Chinese document |

```bash
cd asm_common
cc -O2 -o sokoban host_main.c game.c
./sokoban
cc -O2 -o test_try_move test_try_move.c game.c && ./test_try_move
```

### Replace `sk_try_move` with assembly

With `SK_USE_ASM_TRY_MOVE`, the C `sk_try_move` is not compiled; link the ISA symbol instead:

```bash
cc -O2 -DSK_USE_ASM_TRY_MOVE -o sokoban_asm \
  host_main.c game.c ../asm_x64app1/try_move.o -I.
```

Controls: WASD / z / r / q.
