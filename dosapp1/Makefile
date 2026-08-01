# DJGPP 示例；Turbo C 请用 IDE 加入 src/*.c
CC = gcc
CFLAGS = -std=c99 -Wall -O2 -Isrc
# CFLAGS += -DUSE_MODE13   # DJGPP 图形

sokoban.exe: src/main.c src/game_core.c src/mini_levels.h
	$(CC) $(CFLAGS) -o $@ src/main.c src/game_core.c

clean:
	rm -f sokoban.exe *.o
