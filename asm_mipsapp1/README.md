# asm_mipsapp1 — MIPS32 assembly teaching Sokoban

> [中文版](README.ZH.md)

**Full `sk_try_move` is implemented**, semantics match [`../asm_common/game.c`](../asm_common/game.c).  
Cross-compile is not required in this repo; without the ISA toolchain, play via the C reference host.

## Tools

o32 ABI; mips-linux-gnu-gcc -c

## This directory

| File | Description |
|------|-------------|
| `try_move_mips.S` | **full** `sk_try_move` (layout matches game.h) |
| Playable host | `../asm_common/host_main.c` + `game.c` |
| Self-test | `../asm_common/test_try_move.c` |
| `README.md` | this document (English) |
| `README.ZH.md` | Chinese document |

## Algorithm

1. Fail if already won
2. Compute `nx,ny`; fail if OOB or wall
3. If box: check ahead; push + hist; `moves++`; win check
4. Else walk + hist

## Optional: link assembly `sk_try_move`

```bash
# assemble try_move_mips.S -> try_move.o, then:
cc -O2 -DSK_USE_ASM_TRY_MOVE -o sokoban_asm \
  ../asm_common/host_main.c ../asm_common/game.c try_move.o -I../asm_common
```

On a matching host you may use: `make asm` in this directory (see Makefile).

Default C reference:

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c -I../asm_common
./sokoban
```

Controls: WASD / z / r / q.
