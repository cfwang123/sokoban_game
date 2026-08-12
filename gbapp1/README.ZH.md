# gbapp1 — Game Boy 推箱子（教学）

> [English](readme.md)


**160×144 · 4 灰阶**。逻辑用共享 `game_core`；显示/按键经 `gb_hw.h` 抽象。

| 键 | 功能 |
|----|------|
| 十字 | 移动 |
| B | 撤销 |
| Select | 重置 |
| Start | 下一关 |
| A（过关） | 下一关 |

## 真机 / 模拟器

1. 安装 [GBDK-2020](https://github.com/gbdk-2020/gbdk-2020)  
2. 实现 `gb_hw_*.c` 对接 `joypad` / 背景瓦片  
3. `lcc ... -o sokoban.gb`  
4. 用 BGB / SameBoy / Emulicious 打开  

本仓库**不强制**产出 `.gb`（仅源码与桩）。

对照：`gbaapp1`（GBA Mode3）、`fcapp1`（NES）。
