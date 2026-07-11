# Makefile for sokoban (Linux, gcc, ncursesw)
CC = gcc
CFLAGS = -O2 -Wall -std=c11 -D_GNU_SOURCE -Ilib/cjson
LDFLAGS = -lncursesw

SRCS = main.c game.c levels.c pathfinding.c console_linux.c lib/cjson/cJSON.c
OBJS = $(SRCS:.c=.o)
TARGET = sokoban

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# 显式规则保证 lib/cjson/cJSON.o 在子目录中正确生成
lib/cjson/cJSON.o: lib/cjson/cJSON.c lib/cjson/cJSON.h
	$(CC) $(CFLAGS) -c lib/cjson/cJSON.c -o lib/cjson/cJSON.o

# 头文件依赖
main.o:          main.c console.h levels.h game.h pathfinding.h
game.o:          game.c game.h levels.h
levels.o:        levels.c levels.h lib/cjson/cJSON.h
pathfinding.o:   pathfinding.c pathfinding.h game.h
console_linux.o: console_linux.c console.h

clean:
	rm -f $(OBJS) $(TARGET) lastlevel.ini

.PHONY: all clean
