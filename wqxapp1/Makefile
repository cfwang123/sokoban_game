# 教学用 Makefile：默认目标只检查文件存在，不链接真机固件。
# 若本机有 C 编译器，可 `make host-syntax` 做语法级编译检查（仍无真机 SDK）。

APP     := wqx_sokoban
SRCDIR  := src
INCDIR  := include
SRCS    := $(SRCDIR)/main.c $(SRCDIR)/app.c $(SRCDIR)/game.c \
           $(SRCDIR)/pathfinding.c $(SRCDIR)/ui.c $(SRCDIR)/levels_data.c \
           $(SRCDIR)/wqx_hal_stub.c

.PHONY: all help list host-syntax clean

all: help

help:
	@echo "wqxapp1 — 步步高文曲星推箱子（教学工程）"
	@echo "  make list         列出源文件"
	@echo "  make host-syntax  可选：用主机 gcc -fsyntax-only 检查语法"
	@echo "  真机：用厂商 SDK 替换 wqx_hal_stub.c 后按 SDK 手册链接"
	@echo "详见 readme.md 与 docs/DEVELOPMENT.md"

list:
	@echo Sources:
	@echo $(SRCS) | tr ' ' '\n'

host-syntax:
	gcc -std=c99 -Wall -Wextra -I$(INCDIR) -fsyntax-only $(SRCS)

clean:
	rm -f $(APP) *.o
