# 推箱子 (Sokoban)

> [English](README.md)

一个经典的推箱子益智游戏，提供 **C 语言控制台版** 和 **JavaScript 网页版** 两种实现。

## 功能特点

- 经典推箱子玩法，内置多个关卡
- **C 控制台版** — 轻量级终端游戏
- **网页版** — 浏览器直接游玩，界面简洁
- 内置 **寻路 AI** 辅助解谜
- 关卡求解与批量求解脚本
- 关卡数据使用 JSON 格式，方便编辑

## 项目结构

```
sokoban/
├── c_app/               # C 控制台应用
│   ├── main.c           # 入口
│   ├── game.c/h         # 游戏逻辑
│   ├── levels.c/h       # 关卡管理
│   ├── pathfinding.c/h  # A* 寻路
│   ├── console_win.c    # Windows 控制台渲染
│   ├── console.h        # 控制台抽象层
│   ├── lib/cjson/       # JSON 解析库 (cJSON)
│   └── Makefile         # 构建脚本
├── js/                  # 网页版 (JavaScript)
│   ├── game.js          # 游戏引擎
│   ├── levels.js        # 关卡加载
│   ├── levels_data.js   # 内置关卡数据
│   ├── ai.js            # AI 求解
│   └── pathfinding.js   # 寻路算法
├── scripts/             # 工具脚本
│   ├── solve_levels.js  # 批量求解
│   ├── convert_levels.js
│   └── ...
├── index.html           # 网页入口
├── style.css            # 网页样式
└── levels.json          # 关卡定义
```

## 截图

| C 控制台版 | 网页版 |
|:---:|:---:|
| ![C 推箱子](documents/c_sokoban.png) | ![HTML 推箱子](documents/html_sokoban.png) |

## 快速开始

### 网页版

直接用浏览器打开 `index.html` 即可，无需启动服务器。

### C 控制台版

```bash
cd c_app
make
./sokoban.exe
```

需要 C 编译器（Windows 下推荐 GCC / MinGW）。

## 操作说明

| 按键          | 功能         |
|-------------|------------|
| 方向键 / WASD | 移动玩家      |
| R           | 重置关卡      |
| Z           | 撤销上一步     |
| A           | AI 自动求解   |
| Q / Esc     | 退出         |

## 许可证

MIT
