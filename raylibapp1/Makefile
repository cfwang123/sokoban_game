CC ?= gcc
CFLAGS ?= -O2 -Wall
RAYLIB_FLAGS ?= $(shell pkg-config --cflags --libs raylib 2>/dev/null)
ifeq ($(RAYLIB_FLAGS),)
  RAYLIB_FLAGS := -lraylib -lopengl32 -lgdi32 -lwinmm
endif

all: sokoban

sokoban: main.c
	$(CC) $(CFLAGS) -o $@ main.c $(RAYLIB_FLAGS)

clean:
	rm -f sokoban sokoban.exe

.PHONY: all clean
