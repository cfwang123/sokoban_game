CC = gcc
CFLAGS = -std=c99 -Wall -O2 -Isrc
SRCS = src/main.c src/game_core.c
BIN = sokoban_fb

.PHONY: all clean
all: $(BIN)
$(BIN): $(SRCS) src/mini_levels.h src/game_core.h
	$(CC) $(CFLAGS) -o $@ $(SRCS)
clean:
	rm -f $(BIN)
