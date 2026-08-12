# casioapp1 — Casio 图形计算器推箱子（教学）

> [English](readme.md)


抽象 **128×64** 点阵与 `get_key`，演示如何把同一 `game_core` 接到计算器 Add-In。

真机（示例方向，因型号而异）：

- Casio fx-9860G SDK / Graph 系列 C 插件  
- 将 `put_pixel` / `lcd_flush` / `get_key` 换成 `Bdisp_*` / `GetKey`  
- 入口可能是 `AddIn_main`（定义 `CASIO_ADDIN`）

**关卡必须极小**（`mini_levels.h`）。本仓库不提供厂商 SDK。
