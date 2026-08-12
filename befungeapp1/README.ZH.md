# befungeapp1 — Befunge-93 可玩推箱子

> [English](readme.md)


**游戏逻辑 100% 为 Befunge-93**（`sokoban.bf`）。  
`befunge93.py` / `main.py` 仅为解释器与启动入口，**不含**另一套 Python 游戏实现。

## 关卡

```text
#####
#.$@#
#####
```

一箱一目标；向左推即可过关。

## 运行

```bash
cd befungeapp1
python -X utf8 main.py
```

| 键 | 作用 |
|----|------|
| `a` / `d` | 左 / 右移动（可推箱） |
| `q` 或 EOF | 退出 |

示例输入（先过关再退出）：

```text
a
q
```

## 文件

| 文件 | 说明 |
|------|------|
| `sokoban.bf` | **纯 Befunge-93 游戏源码** |
| `befunge93.py` | Befunge-93 解释器（自动按源码扩展场地宽度） |
| `main.py` | 加载并运行 `sokoban.bf` |
| `gen_sokoban.py` | 维护用：重新生成 `sokoban.bf` |

重新生成：

```bash
python -X utf8 gen_sokoban.py
```

## 实现说明

- 地图存在 Funge-Space 中（`g` / `p` 读写）。
- 主循环在**单行**程序上靠**场地宽度环绕**回到开头；首次运行用标志位初始化坐标。
- 输入 `q` 时向 `(0,0)` 写入 `@`，下一圈环绕即停机。
- 解释器场地宽度 ≥ 程序行长（经典 80 列不够容纳完整逻辑，故采用可扩展宽度，语义仍为 Befunge-93）。

## 与政策的关系

符合仓库约定：目标语言实现玩法；宿主只做解释器。见 [docs/UNSUPPORTED_LANGS.md](../docs/UNSUPPORTED_LANGS.md)。
