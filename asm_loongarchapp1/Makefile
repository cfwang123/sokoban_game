# 默认构建 C 参考实现（无需交叉汇编器）
CC ?= cc
CFLAGS ?= -O2 -Wall
COMMON = ../asm_common

.PHONY: all run clean
all: sokoban
sokoban: $(COMMON)/host_main.c $(COMMON)/game.c $(COMMON)/game.h
	$(CC) $(CFLAGS) -o sokoban $(COMMON)/host_main.c $(COMMON)/game.c -I$(COMMON)

run: sokoban
	./sokoban

clean:
	rm -f sokoban *.o
