# Default: playable C reference. Optional: link ISA sk_try_move when toolchain exists.
CC ?= cc
CFLAGS ?= -O2 -Wall
COMMON = ../asm_common

.PHONY: all run test asm clean
all: sokoban
sokoban: $(COMMON)/host_main.c $(COMMON)/game.c $(COMMON)/game.h
	$(CC) $(CFLAGS) -o sokoban $(COMMON)/host_main.c $(COMMON)/game.c -I$(COMMON)

run: sokoban
	./sokoban

test: $(COMMON)/test_try_move.c $(COMMON)/game.c
	$(CC) $(CFLAGS) -o test_try_move $(COMMON)/test_try_move.c $(COMMON)/game.c -I$(COMMON)
	./test_try_move

# Override ASM_SRC / ASM_CMD in ISA-specific notes below if needed.
# Example (x64 gas): make asm ASM_SRC=try_move_x64.S
asm:
	@echo "See README for assembling sk_try_move and linking with -DSK_USE_ASM_TRY_MOVE"

clean:
	rm -f sokoban test_try_move *.o *.exe sokoban_asm test_asm
