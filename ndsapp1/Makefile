# 真机：devkitPro / devkitARM
#   include $(DEVKITARM)/ds_rules
#   生成 sokoban.nds
.PHONY: help host-syntax
help:
	@echo "ndsapp1 — Nintendo DS Sokoban (teaching)"
	@echo "  Real: devkitARM + libnds -> .nds (melonDS / DeSmuME)"
host-syntax:
	gcc -std=c99 -Wall -Iinclude -fsyntax-only src/main.c src/game_core.c src/nds_hw_stub.c
