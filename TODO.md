# 多平台移植 TODO

> 目标：为推箱子补充多种技术栈的**教学/演示工程**（结构 + 核心代码），不强制本仓库内真机/全量编译通过。  
> 玩法对齐 `html_app`：推箱规则、撤销（仅推箱步）、换关；资源紧平台用迷你关卡集（`scripts/mini_levels.json`）。

## 状态

| # | 目录 | 技术 | 状态 | 说明 |
|---|------|------|------|------|
| 1 | `flutterapp1/` | Flutter / Dart | **完成** | CustomPainter + 点击寻路 + 虚拟键 |
| 2 | `unityapp1/` | Unity C# | **完成** | GameState + GameController（Gizmos） |
| 3 | `rustapp1/` | Rust | **完成** | game 模块 + 终端循环 |
| 4 | `goapp1/` | Go | **完成** | game 包 + 终端；可接 Ebiten |
| 5 | `zigapp1/` | Zig | **完成** | 固定数组 + build.zig |
| 6 | `wxgame1/` | 微信小游戏 | **完成** | game.js + canvas 触摸 |
| 7 | `harmonyapp1/` | HarmonyOS ArkTS | **完成** | GameState.ets + Index 页 |
| 8 | `esp32app1/` | ESP-IDF C | **完成** | game_core + FreeRTOS 桩 |
| 9 | `stm32app1/` | STM32 C | **完成** | Cube 可合并骨架 |
| 10 | `arduinoapp1/` | Arduino | **完成** | 串口 WASD |
| 11 | `linuxfbapp1/` | Linux fbdev | **完成** | `/dev/fb0` + ASCII 回退 |
| 12 | `casioapp1/` | Casio 抽象 | **完成** | 128×64 点阵 HAL |
| 13 | `dosapp1/` | DOS C | **完成** | 文本 / Mode 13h 示意 |

## 进度记录

- 2026-08-02：创建清单并完成 13 个演示工程；根 README 已更新。
- 迷你关卡导出：`scripts/export_mini_levels.py` + `scripts/mini_levels.json`。

## 可选后续

- [ ] 统一从 `levels.json` 一键刷新各平台迷你关
- [ ] 对 `cargo check` / `go build` / `flutter analyze` 做可选 CI
- [ ] 各平台截图
