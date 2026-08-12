# Changelog

## 2026-08-10

- 实现完整 `sk_try_move`（对齐 `asm_common/game.c`：走路 / 推箱 / hist / 判胜）
- 导出符号 `sk_try_move`，可与 `-DSK_USE_ASM_TRY_MOVE` 链接替换 C 实现
- 更新 readme / Makefile 说明

## 初版

- 初版 6502 / 65C02 汇编教学骨架 + 指向 asm_common 可玩实现