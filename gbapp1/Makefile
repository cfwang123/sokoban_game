# 教学 Makefile：默认不链接真实 GBDK。
# 安装 GBDK 后示例：
#   lcc -Wa-l -Wl-m -Wl-j -DUSE_GBDK -o sokoban.gb src/*.c

.PHONY: help list host-syntax
help:
	@echo "gbapp1 — Game Boy Sokoban (teaching)"
	@echo "  make list"
	@echo "  Real build: GBDK-2020 lcc -> sokoban.gb"
list:
	@echo src/main.c src/game_core.c src/gb_hw_stub.c
host-syntax:
	gcc -std=c99 -Wall -Iinclude -fsyntax-only src/main.c src/game_core.c src/gb_hw_stub.c
