# brainfuckapp1 — Brainfuck 推箱子（教学）

> [English](README.md)


纯 **Brainfuck** 实现的迷你关卡终端版；仓库内附带 Python 解释器，无需另装 `bf` 工具即可运行。

```bash
cd brainfuckapp1
python -X utf8 main.py
```

也可用任意兼容的 Brainfuck 解释器直接跑 `sokoban.bf`（忽略非 `+-<>[],.` 字符）。

键位：WASD 移动，z 撤销，r 重置，q 退出。

## 文件

| 文件 | 说明 |
|------|------|
| `sokoban.bf` | Brainfuck 源码（由生成器展开；约 100 万条指令） |
| `main.py` | 小型 BF 解释器 + 行缓冲输入 |
| `README.ZH.md` | 本说明（中文） |
| `README.md` | English |

重新生成 `sokoban.bf`（维护用）：

```bash
python -X utf8 scripts/_gen_brainfuck_sokoban.py
```

## 说明

- 关卡与其它 `*app1` 教学版相同（7×7 迷你图）。
- 撤销与其它版本一致：回退到并包含最近一次推箱。
- 注释行不得包含 `+ - < > [ ] , .`，否则会被当成指令执行。
