# 需已安装 SDL2 开发库
CC ?= gcc
CFLAGS ?= -O2 -Wall
SDL_CFLAGS := $(shell pkg-config --cflags sdl2 2>/dev/null)
SDL_LIBS := $(shell pkg-config --libs sdl2 2>/dev/null)
ifeq ($(SDL_LIBS),)
  SDL_CFLAGS :=
  SDL_LIBS := -lSDL2
endif

all: sokoban

sokoban: main.c
	$(CC) $(CFLAGS) $(SDL_CFLAGS) -o $@ main.c $(SDL_LIBS)

clean:
	rm -f sokoban sokoban.exe

.PHONY: all clean
