# befungeapp1 — Befunge 推箱子（完整游戏）

**纯 Befunge** 实现迷你关卡（与 `brainfuckapp1` 同一政策：玩法在目标语言里，Python 只做解释器）。

```bash
cd befungeapp1
python -X utf8 main.py
python -X utf8 main.py --test
# 或
python -X utf8 befunge93.py sokoban.bf
```

| 键 | 动作 |
|----|------|
| WASD | 移动 / 推箱 |
| z | 撤销到并包含最近一次推箱 |
| r | 重置 |
| q | 退出 |

## 文件

| 文件 | 说明 |
|------|------|
| `sokoban.bf` | **纯 Befunge** 完整游戏（生成器展开；playfield 可大于经典 80×25） |
| `befunge93.py` | Befunge-93 指令集解释器（按源码自动扩展场地） |
| `main.py` | 加载并运行 `sokoban.bf`；`--test` 自检 |

重新生成 `sokoban.bf`：

```bash
python -X utf8 scripts/_gen_befunge_sokoban.py
```

## 说明

- 方言：指令与 [Befunge-93](https://esolangs.org/wiki/Befunge) 相同；场地按程序加宽加高（经典 80×25 装不下完整交互循环）。
- 注释行以 `;;` 开头，加载时剥离。
- 数据区用 `p`/`g` 存变量、地图与撤销历史。
