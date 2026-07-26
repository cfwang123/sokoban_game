# 推箱子 (Sokoban)

> [English](README.md)

一个经典的推箱子益智游戏，提供控制台、网页与多种主机 homebrew 实现。

## 功能特点

- 经典推箱子玩法，内置多个关卡（`levels.json`）
- **C 控制台版** — 轻量级终端游戏
- **2D / 3D 网页版** — 浏览器游玩（3D 基于 three.js）
- **FC / NES** — `fcapp1/`（cc65，`sokoban.nes`）
- **GBA** — `gbaapp1/`（裸机 Mode 3，`sokoban.gba`）
- **PSP** — `pspapp1/`（pspdev + sceGu，`EBOOT.PBP`）
- 内置寻路 / 答案回放（视平台而定）
- 关卡数据 JSON，便于编辑与转换

## 项目结构

```
sokoban/
├── c_app/               # C 控制台（Windows）
├── sokoban_linux/       # C 控制台（Linux）
├── html_app/            # 2D 网页
├── html_3dapp/          # 3D 网页（three.js）
├── fcapp1/              # FC / NES homebrew
├── gbaapp1/             # GBA homebrew
├── pspapp1/             # PSP homebrew
├── scripts/             # 求解与转换脚本
├── levels.json          # 关卡定义
└── documents/           # 截图等
```

## 截图

| C 控制台版 | 2D 网页版 | 3D 网页版 |
|:---:|:---:|:---:|
| ![C 推箱子](documents/c_sokoban.png) | ![HTML 推箱子](documents/html_sokoban.png) | ![3D 推箱子](documents/html_3d.png) |

## 快速开始

### 2D 网页版

直接用浏览器打开 `index.html` 即可，无需启动服务器。

### 3D 网页版

建议通过本地 HTTP 服务器打开 `html_3dapp/index.html`。

示例：

```bash
cd html_3dapp
python -m http.server 8765
```

然后访问 `http://localhost:8765/`。

### C 控制台版

```bash
cd c_app
make
./sokoban.exe
```

需要 C 编译器（Windows 下推荐 GCC / MinGW）。

### FC / NES 版

见 [fcapp1/README.md](fcapp1/README.md)。用任意 FC 模拟器打开 `fcapp1/sokoban.nes`。

```bat
cd fcapp1
build.bat
```

### GBA 版

见 [gbaapp1/README.md](gbaapp1/README.md)。用 mGBA 等打开 `gbaapp1/sokoban.gba`。

```bat
cd gbaapp1
build.bat
```

### PSP 版

见 [pspapp1/README.md](pspapp1/README.md)。用 PPSSPP 打开 `pspapp1/EBOOT.PBP`。

推荐 **WSL Ubuntu + ~/pspdev**：

```bat
cd pspapp1
build_wsl.bat
```

## 操作说明

### C 控制台版

| 按键             | 功能          |
|----------------|-------------|
| 方向键 / WASD    | 移动玩家       |
| Z              | 撤销上一步      |
| R              | 重置关卡       |
| F1             | AI 自动求解    |
| F2             | 选择关卡       |
| Space          | 下一关（通关后）  |
| PageUp         | 上一关        |
| PageDown       | 下一关        |
| Q / Esc        | 退出          |

### 2D 网页版

| 按键             | 功能          |
|----------------|-------------|
| 方向键 / WASD    | 移动玩家       |
| Z              | 撤销上一步      |
| R              | 重置关卡       |
| F1             | 查看答案       |
| Space          | 下一关（通关后）  |
| PageUp         | 上一关        |
| PageDown       | 下一关        |

### 3D 网页版

| 按键 / 鼠标       | 功能          |
|----------------|-------------|
| 方向键 / WASD    | 移动玩家       |
| Z              | 撤销上一步      |
| R              | 重置关卡       |
| F1             | 查看答案       |
| Space          | 下一关（通关后）  |
| PageUp         | 上一关        |
| PageDown       | 下一关        |
| 鼠标拖拽         | 旋转视角       |

## 许可证

MIT
