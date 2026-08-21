# pygameapp1 — Pygame 推箱子（仿 html_app 2D）

> [English](README.md)


用 [Pygame](https://www.pygame.org/) 复刻网页 2D 版（`html_app/`）的画面与操作。

## 功能

| 能力 | 说明 |
|------|------|
| 关卡 | 读取仓库根目录 `levels.json`（或本目录副本） |
| 渲染 | 地板 / 墙高光 / 目标点 / 箱子（到位变绿）/ 玩家，配色对齐网页 |
| 键盘 | 方向键 · WASD，按住连发 |
| 鼠标 | 点击空地 BFS 寻路；点击相邻箱子推一格 |
| 撤销 | 只回退到上一次推箱（与网页一致） |
| 答案 | 有 `solution` 的关可 F1 动画回放 |
| 进度 | `lastlevel.ini` 记住上次关卡 |

## 运行

```bash
cd pygameapp1
pip install -r requirements.txt
python -X utf8 main.py
```

## 键位

| 键 | 功能 |
|----|------|
| 方向键 / WASD | 移动 |
| Z | 撤销推箱 |
| R | 重置本关 |
| F1 | 查看 / 停止答案 |
| PageUp / P | 上一关 |
| PageDown / N | 下一关 |
| 空格 | 通关后下一关 |
| H | 帮助 |

## 结构

```
pygameapp1/
├── main.py           # 窗口、输入、绘制
├── game.py           # 状态机 + 寻路
├── requirements.txt
├── README.ZH.md
└── README.md
```

对照：

- 玩法与配色：[`../html_app`](../html_app)
- 纯终端 Python：[`../pythonapp1`](../pythonapp1)
