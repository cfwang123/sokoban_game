# 未提供可玩移植的语言

> 政策：推箱子须用**目标语言**实现；禁止用 Python（或其它宿主）另写一套游戏逻辑冒充该语言 demo。  
> 若语言难以在本仓库内完成「可交互 + 可维护 + 可验证」的原生实现，则**不建目录**，仅在此（及 [TODO.md](../TODO.md)）标注原因。

## 中文编程语言

| 语言 | 原因 |
|------|------|
| **易语言** | 依赖闭源 IDE/编译器，无法在开源仓库内原生编译运行完整工程 |
| **文言 (wenyan-lang)** | 可转 JS/Python，但用纯文言写完整交互终端游戏不现实；不宜用宿主语言代替 |
| **PerlYuYan** | 依赖 CPAN `Lingua::Sinica::PerlYuYan` 过滤；完整游戏若用普通 Perl 则不算该语言 |

## 古典 / 数组语言

| 语言 | 原因 |
|------|------|
| **APL** | 完整可玩需本机 APL 环境与大量调试；曾用 Python 代替已删除 |
| **Factor** | 同上；曾用 Python 代替已删除 |

## 深奥语言（Esolang）— 无法实现

下列语言在本仓库约束下**无法**提供「纯该语言驱动的可交互推箱子」，**不设目录**：

| 语言 | 原因摘要 |
|------|----------|
| **///（三斜杠）** | 无运行时输入；交互必须宿主注入 |
| **INTERCAL** | 故意难用；工具链与交互 I/O 不适合本教学规模 |
| **Malbolge** | 几乎不可手写完整程序 |
| **Piet** | 图像编程，工具链与体量不适合文本仓库 |
| ~~**JSFuck**~~ | **已实现** → `jsfuckapp1/` |
| ~~**Befunge**~~ | **已实现** → `befungeapp1/`（纯 `sokoban.bf` + 解释器） |
| ~~**Unreadable**~~ | **已实现** → `unreadableapp1/`（纯 `'`/`"` 游戏 + Python 解释器） |
| **Chef** | 菜谱式栈语言，不适合交互主循环 |
| **FALSE** | 极简栈语言，完整交互游戏不现实 |
| **LOLCODE** | 方言/工具链不稳定，不宜假冒完整原生工程 |
| **Whitespace** | 纯空白字符，难审阅、难协作 |
| **Shakespeare (SPL)** | 戏剧语法，不适合完整交互游戏 |
| **Chicken** | 仅 “chicken” 词，完整游戏不现实 |
| **Unlambda** | 组合子编码状态过重 |
| **Thue** | 无输入的串重写，交互需宿主 |
| **二元 Lambda 演算 (BLC)** | 位流编码，教学可玩成本过高 |
| **Subleq / OISC** | 机器码级，不适合手写维护完整游戏 |
| **MarioLANG** | 2D 规范模糊，完整交互体量不适合 |

## 仍保留且符合政策的相关目录

| 目录 | 说明 |
|------|------|
| `brainfuckapp1/` | **Brainfuck** — 游戏为纯 BF；Python 仅为解释器（允许） |
| `befungeapp1/` | **Befunge** — 游戏为纯 `.bf`；Python 仅为解释器（允许；场地可大于经典 80×25） |
| `jsfuckapp1/` | **JSFuck** — `try_move` 为纯 `[]()!+`（`generate.js` 生成）；宿主只负责 UI |
| `unreadableapp1/` | **Unreadable** — 游戏为纯 `'`/`"`；Python 仅为解释器 |
| `parenthesishellapp1/` | **Parenthesis Hell** — Python 解释器；状态为 PH Cons/Nil；纯 `()` 示例 `hello.ph` |
| `xiyuyanapp1/` | **习语言**（中文 C 宏）— 游戏源码即中文关键字 C |
| `bingzhengzhengapp1/` | **丙正正**（中文 C++ 宏） |
| `caomangapp1/` | **草蟒** — 逻辑在 `.草蟒`；`main.py` 仅为关键字翻译运行时 |
| `pythonapp1/` 等 | 目标语言本身就是 Python / 其它通用语言的原生实现 |

**允许的模式**：「目标语言源码实现玩法 + 仓库内小型解释器/翻译层仅负责执行」。  
**禁止的模式**：「Python（等）实现玩法 + 旁边放一份该语言骨架冒充 demo」。
