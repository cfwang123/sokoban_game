# unreadableapp1 — Unreadable 推箱子（完整游戏）

> [English](README.md)


**纯 [Unreadable](https://esolangs.org/wiki/Unreadable)** 实现迷你关卡（与 `brainfuckapp1` / `befungeapp1` 同一政策：玩法在目标语言里，Python 只做解释器）。

源码仅由 `'` 与 `"` 组成；命令由引号数量决定（PRINT / INC / ONE / DO / WHILE / SET / GET / DEC / IF / IN）。

```bash
cd unreadableapp1
python -X utf8 main.py
python -X utf8 main.py --test
# 或
python -X utf8 interpreter.py sokoban.unr
```

| 键 | 动作 |
|----|------|
| WASD | 移动 / 推箱 |
| z | 撤销 |
| r | 重置 |
| q | 退出 |

## 文件

| 文件 | 说明 |
|------|------|
| `sokoban.unr` | **纯 Unreadable** 完整游戏（脚本生成） |
| `interpreter.py` | Unreadable 解释器（解析 + 求值；宿主不写玩法） |
| `main.py` | 加载并运行；`--test` 自检；`--rebuild` 重新生成 |

重新生成 `sokoban.unr`：

```bash
python -X utf8 main.py --rebuild
# 或
python -X utf8 scripts/_gen_unreadable_sokoban.py
```

## 说明

- 方言与 [esolangs Unreadable](https://esolangs.org/wiki/Unreadable) 一致；多条顶层表达式顺序执行。
- 地图、玩家、撤销历史等全部存在 Unreadable 的变量数组中（`SET`/`GET`）。
- 因语言只有 `+1`/`-1` 算术，渲染与比较较慢，属预期行为。
