# Makefile for sokoban.exe (Windows, gcc)
CC = gcc
CFLAGS = -O2 -Wall -std=c11 -Ilib/cjson
LDFLAGS =

SRCS = main.c game.c levels.c pathfinding.c console_win.c lib/cjson/cJSON.c
OBJS = $(SRCS:.c=.o)
TARGET = sokoban.exe

all: $(TARGET) levels.json

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# 显式规则保证 lib/cjson/cJSON.o 在子目录中正确生成
lib/cjson/cJSON.o: lib/cjson/cJSON.c lib/cjson/cJSON.h
	$(CC) $(CFLAGS) -c lib/cjson/cJSON.c -o lib/cjson/cJSON.o

# 头文件依赖
main.o:        main.c console.h levels.h game.h pathfinding.h
game.o:        game.c game.h levels.h
levels.o:      levels.c levels.h lib/cjson/cJSON.h
pathfinding.o: pathfinding.c pathfinding.h game.h
console_win.o: console_win.c console.h

# 把上级目录的 levels.json 拷贝到 exe 同目录
levels.json: ../levels.json
	copy /Y ..\levels.json levels.json

clean:
	del /Q $(OBJS) $(TARGET) levels.json lastlevel.ini 2>nul

.PHONY: all clean
