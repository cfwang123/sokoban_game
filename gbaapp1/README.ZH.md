# 推箱子 · GBA 版（gbaapp1）

> [English](README.md)


将 `html_app` / `fcapp1` 的推箱子移植为 **Game Boy Advance** ROM。  
画面为 **Mode 3 真彩 16×16 贴图** + 阴影字体 HUD，画质明显高于 FC 8×8 点阵。

参考工程：`game/gba/tower_gba`（裸机 + EWRAM 离屏缓冲）。

## 运行

用 mGBA / VBA-M / RetroArch 打开：

```
gbaapp1/sokoban.gba
```

## 操作

| 键 | 功能 |
|----|------|
| **← →**（标题） | 选关 |
| **Start / A**（标题） | 开始 |
| **十字键** | 移动 / 推箱（支持连发） |
| **B** | 撤销 |
| **Select** | 重置本关 |
| **Start**（游戏中） | 菜单：RESET / NEXT / ANSWER |
| **A**（菜单） | 确认 |
| **B**（菜单） | 返回 |
| **A**（过关） | 下一关 |
| **B**（过关） | 回标题 |
| **B/Start**（DEMO） | 取消答案回放 |

## 画面图例

| 元素 | 表现 |
|------|------|
| 墙 | 灰石砖 + 斜接阴影 |
| 地板 | 深蓝地砖 |
| 目标 | 红色发光圆盘 |
| 箱子 | 木箱 + 金属箍 + X |
| 箱在目标 | 绿色木箱 |
| 玩家 | 带表情的小人精灵 |

## 重新编译

依赖：

- `arm-none-eabi-gcc`（加入 PATH，或设置 `DEVKITARM` / `ARM_NONE_EABI_PREFIX`）
- Python 3
- Node.js（`gbafix.js`）

```bat
cd gbaapp1
build.bat
```

或：

```bash
make
```

## 工程结构

```
gbaapp1/
  sokoban.gba       成品 ROM
  build.bat / Makefile
  gba.ld            链接脚本
  include/          gba.h game.h gfx.h ...
  src/              main/game/gfx/sound/crt0 + 生成数据
  tools/
    gen_tiles.py    16x16 精致贴图
    gen_levels.py   从 ../levels.json 打包关卡与答案
    gbafix.js       ROM 头校验
```

## 技术说明

| 项目 | 内容 |
|------|------|
| CPU | ARM7TDMI @ 16.78 MHz |
| 显示 | Mode 3，240×160，15-bit 色 |
| 渲染 | EWRAM 离屏缓冲 + VBlank DMA 翻页 |
| 逻辑 | C 全逻辑：推箱/撤销/菜单/答案回放/镜头跟随 |
| 关卡 | 默认约 60 关（优先带答案） |
| 音频 | PSG 方波简易音效 |

### 与 FC 版对比

| | FC (fcapp1) | GBA (gbaapp1) |
|--|-------------|---------------|
| 分辨率 | 256×240 点阵 | 240×160 真彩 |
| 格子 | 8×8 单色 | **16×16 渐变/阴影** |
| 颜色 | 同时 4 色级 | **32768 色** |
| 镜头 | 无 | 大关卡镜头跟随 |
| 缓冲 | 直接写 VRAM | 双缓冲无闪烁 |
