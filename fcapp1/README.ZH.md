# FC 推箱子（fcapp1）

> [English](readme.md)


将 `html_app` 的推箱子玩法移植到 **NES/FC**，工程结构参考 `game/fc_mario`。

- **游戏逻辑用 C**（cc65）
- 汇编仅保留：iNES 头、Reset 启动、NMI、CHR 嵌入

成品 ROM：`sokoban.nes`（NROM-256，约 40KB）

## 运行

用任意 NES/FC 模拟器打开：

```
fcapp1/sokoban.nes
```

推荐：Mesen、FCEUX、Nestopia、RetroArch。

## 操作

| 按键 | 功能 |
|------|------|
| **← →**（标题） | 选关 |
| **Start / A**（标题） | 开始 |
| **方向键** | 移动 / 推箱子 |
| **B** | 撤销（先撤销走路，再撤销最近一次推箱） |
| **Select** | 重置本关（快捷） |
| **Start**（游戏中） | 打开菜单 |
| **↑ ↓**（菜单） | 选择：RESET / NEXT / ANS |
| **A / Start**（菜单） | 确认 |
| **B**（菜单） | 关闭菜单 |
| **B / Start**（答案回放） | 取消回放 |
| **Start / A**（通关） | 下一关 |
| **B**（通关） | 回标题 |

菜单项：

| 项 | 含义 |
|----|------|
| **RESET** | 重置本关 |
| **NEXT** | 下一关 |
| **ANS** | 播放预置答案（无答案时无效并提示音） |

HUD：`L` 关卡号 · `M` 推箱步数 · `G` 已入目标/总箱子

## 重新编译

依赖：

- [cc65](https://cc65.github.io/) V2.19+（`cc65` / `ca65` / `ld65` 在 PATH，或设置 `CC65_HOME`，或放到 `fcapp1/tools/cc65/`）
- Python 3（生成 CHR 与关卡数据）
- 上级目录的 `levels.json`

```bat
cd fcapp1
build.bat
```

流程：

1. `tools/make_chr.py` → `chr/tiles.chr`
2. `tools/gen_levels.py` → `src/levels.c`（从 `../levels.json` 筛选 ≤20×18 的关卡，最多 80 关）
3. cc65 编译 `main.c` / `music.c` / `levels.c`
4. ca65 汇编 + ld65 链接 → `sokoban.nes`

## 工程结构

```
fcapp1/
  sokoban.nes       成品 ROM
  build.bat         一键编译
  nrom256.cfg       ld65：32KB PRG + 8KB CHR
  chr/tiles.chr     像素图
  src/
    main.c          主逻辑（标题/关卡/移动/撤销/绘制）
    music.c         8bit BGM + 音效
    levels.c        关卡数据（脚本生成）
    nes.h / game.h  寄存器与声明
    header.s        iNES 头
    reset.s         启动、清 RAM、调色板、进 main
    nmi.s           OAM DMA + 音乐节拍
    chr.s           嵌入 CHR
  tools/
    make_chr.py
    gen_levels.py
```

## 与 html_app 的对应关系

| html_app | fcapp1 |
|----------|--------|
| `game.js` 移动/推箱/撤销/过关 | `main.c` |
| `levels_data.js` | `levels.c`（半字节打包） |
| Canvas 绘制 | 背景 Nametable + 玩家精灵 |
| 键盘 WASD | 手柄方向 |
| 鼠标寻路 / AI 求解 | 未移植（FC 算力与输入限制） |
| 查看答案 | 未移植（ROM 体积） |

规则对齐：

- 撞墙无效
- 推箱：前方无墙/箱才可推，**计 1 步**
- 纯走路**不计步**
- 撤销：连续撤销走路，直到撤销一次推箱（同网页版）
- 全部箱子在目标上即过关

## 技术说明

| 项目 | 内容 |
|------|------|
| 主机 | NES / Famicom（6502） |
| 语言 | **C（主逻辑）** + 少量汇编 |
| Mapper | 0（NROM） |
| PRG | 32 KB |
| CHR | 8 KB |
| 工具链 | cc65 / ca65 / ld65 + `none.lib` |
| 格子 | 1 cell = 1 个 8×8 背景图块 |
| 地图 RAM | 最大 20×18，`map_cells[]` 位标志墙/目标/箱 |

### 为何还留一点汇编？

与 `fc_mario` 相同：

1. **iNES 头** — 二进制布局  
2. **Reset** — 关中断、清 RAM、设 C 栈 `c_sp`、跳转 `_main`  
3. **NMI** — vblank 里 OAM DMA  
4. **CHR** — `.incbin` 像素 ROM  

关卡解析、移动、撤销、过关判定、标题与绘制均在 **C** 中。

## 工具链配置

`build.bat` 按以下顺序查找 cc65（任选其一即可）：

1. 环境变量 `CC65_HOME`（指向含 `bin/`、`lib/` 的安装根目录）
2. 本仓库 `fcapp1/tools/cc65/`（可选本地拷贝，勿提交）
3. 已加入 `PATH` 的 `cc65` / `ca65` / `ld65`
