# ndsapp1 — Nintendo DS 推箱子（教学）

> [English](README.md)


**双屏**：上屏棋盘，下屏 HUD + 触屏方向键。逻辑 `game_core`，显示 `nds_hw.h`。

| 输入 | 功能 |
|------|------|
| 十字 / 触屏 D-pad | 移动 |
| B | 撤销 |
| X | 重置 |
| Y | 下一关 |
| A（过关） | 下一关 |

## 真机

1. 安装 [devkitPro](https://devkitpro.org/)（devkitARM + libnds）  
2. 实现 `nds_hw_*.c` 调用 `scanKeys` / `touchRead` / VRAM  
3. 构建 `.nds`，用 melonDS / DeSmuME 运行  

本仓库不强制产出 `.nds`。
