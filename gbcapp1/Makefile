.PHONY: help host-syntax
help:
	@echo "gbcapp1 — Game Boy Color Sokoban (teaching)"
	@echo "  GBDK: lcc -Wm-yc ... for CGB mode"
host-syntax:
	gcc -std=c99 -Wall -Iinclude -fsyntax-only src/main.c src/game_core.c src/gbc_hw_stub.c
