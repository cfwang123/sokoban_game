CC ?= gcc
CFLAGS ?= -O2 -Wall
COMMON = ../asm_common
ASM_SRC = try_move_x64.S

.PHONY: all run test asm clean
all: sokoban
sokoban: $(COMMON)/host_main.c $(COMMON)/game.c $(COMMON)/game.h
	$(CC) $(CFLAGS) -o sokoban $(COMMON)/host_main.c $(COMMON)/game.c -I$(COMMON)

run: sokoban
	./sokoban

test: $(COMMON)/test_try_move.c $(COMMON)/game.c
	$(CC) $(CFLAGS) -o test_try_move $(COMMON)/test_try_move.c $(COMMON)/game.c -I$(COMMON)
	./test_try_move

# Link full assembly sk_try_move (Win64 MinGW or System V depending on host)
asm: $(ASM_SRC)
	$(CC) -c $(ASM_SRC) -o try_move.o
	$(CC) $(CFLAGS) -DSK_USE_ASM_TRY_MOVE -o sokoban_asm \
	  $(COMMON)/host_main.c $(COMMON)/game.c try_move.o -I$(COMMON)
	$(CC) $(CFLAGS) -DSK_USE_ASM_TRY_MOVE -o test_asm \
	  $(COMMON)/test_try_move.c $(COMMON)/game.c try_move.o -I$(COMMON)
	./test_asm

clean:
	rm -f sokoban sokoban_asm test_try_move test_asm *.o *.exe
