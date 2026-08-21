# parenthesishellapp1 — Parenthesis Hell 推箱子

> [English](README.md)


[Parenthesis Hell](https://esolangs.org/wiki/Parenthesis_Hell)：Lisp 风格 esolang，**代码与数据都只有嵌套括号** `()`。  
本目录提供 **Python 解释器** + 可玩迷你关卡。

## 运行

```bash
cd parenthesishellapp1
python -X utf8 main.py
python -X utf8 main.py --test
```

键位：WASD 移动，`z` 撤销，`r` 重置，`q` 退出。

## 文件

| 文件 | 说明 |
|------|------|
| `ph.py` | **Parenthesis Hell 解释器**（parse / eval / ASCII 编解码） |
| `hello.ph` | 纯 `()` Hello world（维基示例） |
| `sokoban.ph` | 纯 `()` 程序（默认 identity：返回输入状态） |
| `main.py` | 交互主机 + 用 PH `Cons`/`Nil` 树表示的棋盘状态 |
| `generate.py` | 重新写入默认 `sokoban.ph` |
| `README.ZH.md` | 本说明（中文） |
| `README.md` | English |

## 语言要点

| 构造 | 含义 |
|------|------|
| `()` | 在表达式位置：当前输入；作函数名：quote |
| `(())` | letrec |
| `((()))` | car |
| `(()())` | cdr |
| `((())())` | cons |
| `(()()())` | if |
| `(((())))` | eval |

程序是**单个表达式**，以输入值为参数，输出为求值结果。无流式 `getchar`；交互循环由主机提供。

ASCII 字符串按位编码进括号树（与 [qpliu/esolang](https://github.com/qpliu/esolang) 一致）。`hello.ph` 可单独验证：

```bash
python -X utf8 -c "from ph import run_source; from pathlib import Path; print(repr(run_source(Path('hello.ph').read_text(encoding='utf-8'))))"
```

## 与「纯 PH 整局」的边界

Parenthesis Hell 适合纯函数变换，不适合自带交互主循环。本实现：

- **状态** = 合法 PH 值（`Cons` / `Nil` 树，可用 `value_to_source` 打印为纯括号）；
- **每步**后将状态送入 `sokoban.ph`（默认同等 `()` / cat）求值，保证状态始终是 PH 语义下的值；
- **推箱规则**在主机中对 PH 值结构进行（与 Brainfuck 主机读 `.` 输出类似：解释器负责语言，主机负责会话）；
- 纯 PH 示例：`hello.ph`、quote/cat 自检（`--test`）。

完整把 try_move 写成手写 letrec 巨表达式体积大、难维护；解释器与值模型已按规范实现，可在此基础上继续生成更完整的纯 PH 步进程序。
