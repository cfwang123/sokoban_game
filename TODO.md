# 多平台 / 多语言移植清单

教学终端版统一约定：迷你关卡、WASD 移动、`z` 撤销、`r` 重置、`q` 退出。

## 古典 / 历史语言终端版

| 目录 | 语言 | 状态 |
|------|------|------|
| `lispapp1/` | Common Lisp | ✅ |
| `schemeapp1/` | Scheme | ✅ |
| `cobolapp1/` | COBOL | ✅ |
| `fortranapp1/` | Fortran | ✅ |
| `pascalapp1/` | Pascal | ✅ |
| `prologapp1/` | Prolog | ✅ |
| `basicapp1/` | FreeBASIC | ✅ |
| `adaapp1/` | Ada | ✅ |
| `forthapp1/` | Forth | ✅ |
| `tclapp1/` | Tcl | ✅ |
| `smalltalkapp1/` | Smalltalk | ✅ |
| `modula2app1/` | Modula-2 | ✅ |
| `algolapp1/` | Algol 68 | ✅ |
| `iconapp1/` | Icon | ✅ |
| `rexxapp1/` | REXX | ✅ |
| `logoapp1/` | Logo | ✅ |

## 现代语言终端版

| 目录 | 语言 | 状态 |
|------|------|------|
| `ocamlapp1/` | OCaml | ✅ |
| `clojureapp1/` | Clojure | ✅ |
| `fsharpapp1/` | F# | ✅ |
| `scalaapp1/` | Scala | ✅ |
| `elixirapp1/` | Elixir | ✅ |
| `erlangapp1/` | Erlang | ✅ |
| `nimapp1/` | Nim | ✅ |
| `crystalapp1/` | Crystal | ✅ |
| `dlangapp1/` | D | ✅ |
| `swiftapp1/` | Swift CLI | ✅ |
| `dartapp1/` | Dart CLI | ✅ |
| `juliaapp1/` | Julia | ✅ |
| `powershellapp1/` | PowerShell | ✅ |
| `bashapp1/` | Bash | ✅ |
| `cmdapp1/` | Windows CMD / 批处理（main.cmd） | ✅ |
| `awkapp1/` | AWK | ✅ |
| `sqlapp1/` | SQL / SQLite | ✅ |
| `cppapp1/` | C++ | ✅ |
| `groovyapp1/` | Groovy | ✅ |
| `vapp1/` | V | ✅ |
| `odinapp1/` | Odin | ✅ |
| `vbapp1/` | Visual Basic .NET | ✅ |
| `vbaapp1/` | VBA（Excel 宏） | ✅ |
| `vb6app1/` | Visual Basic 6.0 | ✅ |

## 中文编程语言（目标语言实现）

| 目录 | 语言 | 状态 |
|------|------|------|
| `xiyuyanapp1/` | 习语言（中文 C 宏，`main.c`） | ✅ |
| `bingzhengzhengapp1/` | 丙正正（中文 C++ 宏，`main.cpp`） | ✅ |
| `caomangapp1/` | 草蟒（`.草蟒` 逻辑 + 关键字翻译运行时） | ✅ |

易语言 / 文言 / PerlYuYan 等**不设目录**，见 [docs/UNSUPPORTED_LANGS.md](docs/UNSUPPORTED_LANGS.md)。

## 深奥编程语言（Esolang）

政策：游戏须用**目标语言**实现；宿主仅可作解释器，不可另写一套游戏。

### 已实现

| 目录 | 语言 | 状态 |
|------|------|------|
| `brainfuckapp1/` | Brainfuck（纯 BF + 仓库内解释器） | ✅ |
| `befungeapp1/` | Befunge（纯 `.bf` + 仓库内解释器） | ✅ |
| `jsfuckapp1/` | JSFuck（`try_move` 纯 `[]()!+`，`generate.js` 生成；Node / play.html） | ✅ |

### 无法实现（不建目录）

Chef、FALSE、MarioLANG、LOLCODE、Whitespace、Shakespeare、INTERCAL、Malbolge、Piet、Chicken、Unlambda、Thue、///、BLC、Subleq、APL、Factor 等：见 **[docs/UNSUPPORTED_LANGS.md](docs/UNSUPPORTED_LANGS.md)**。

## GUI / TUI 教学（不强制本仓库编译）

| 目录 | 技术 | 状态 |
|------|------|------|
| `win32app1/` | C Win32 API | ✅ |
| `mfcapp1/` | C++/MFC Doc-View | ✅ |
| `tkinterapp1/` | Python Tkinter（标准库） | ✅ |
| `pyqtapp1/` | Python PyQt5/6 / PySide6 | ✅ |
| `winformsapp1/` | C# WinForms | ✅ |
| `wpfapp1/` | C# WPF | ✅ |
| `avaloniaapp1/` | C# Avalonia | ✅ |
| `csharptuiapp1/` | C# 终端 TUI（ANSI） | ✅ |
| `reactapp1/` | React（CDN，无构建） | ✅ |
| `vueapp1/` | Vue 3（CDN，无构建） | ✅ |
| `angularapp1/` | Angular 组件源码 + play.html | ✅ |
| `cocos2dapp1/` | Cocos2d 风格 Canvas 场景 | ✅ |
| `x11app1/` | C X11/Xlib | ✅ |
| `gtkapp1/` | C GTK3（gtx→GTK） | ✅ |
| `blazorapp1/` | C# Blazor WebAssembly | ✅ |
| `mauiapp1/` | .NET MAUI | ✅ |
| `winui3app1/` | WinUI 3 | ✅ |
| `monoapp1/` | Mono / mcs | ✅ |
| `netaotapp1/` | .NET Native AOT | ✅ |

## 汇编教学（C 参考 + 各 ISA 完整 `sk_try_move`）

| 目录 | ISA | 状态 |
|------|------|------|
| `asm_common/` | C 可玩参考 + `test_try_move` | ✅ |
| `asm_x86app1/` | x86 (IA-32) 完整 `sk_try_move` | ✅ |
| `asm_x64app1/` | x86-64 完整 `sk_try_move`（本机可 `make asm`） | ✅ |
| `asm_armapp1/` | ARM32 完整 `sk_try_move` | ✅ |
| `asm_thumbapp1/` | Thumb / Thumb-2 完整 `sk_try_move` | ✅ |
| `asm_aarch64app1/` | AArch64 完整 `sk_try_move` | ✅ |
| `asm_riscvapp1/` | RISC-V 完整 `sk_try_move` | ✅ |
| `asm_mipsapp1/` | MIPS32 完整 `sk_try_move` | ✅ |
| `asm_ppcapp1/` | PowerPC 完整 `sk_try_move` | ✅ |
| `asm_avrapp1/` | AVR 完整 `sk_try_move` | ✅ |
| `asm_z80app1/` | Z80 完整 `sk_try_move` | ✅ |
| `asm_6502app1/` | 6502 完整 `sk_try_move` | ✅ |
| `asm_loongarchapp1/` | LoongArch 完整 `sk_try_move` | ✅ |
| `asm_wasmapp1/` | WebAssembly / WAT 完整核心 | ✅ |

已有相关：`qtapp1`（C++ Qt）、`pygameapp1`、`html_app`、`csharpapp1`（行式 CLI）。

## 既有（本清单不重复）

Python / PHP / Lua / Node.js / Ruby / Java / C# / Kotlin / Perl / R / Haskell / Rust / Go / Zig 及桌面/主机/扩展等，见根目录 README。

## 说明

- 多数为教学演示，不强制本机安装对应工具链。
- **政策**：须用**目标语言**实现游戏；禁止用 Python 等宿主另写一套逻辑冒充该语言 demo。实现不了的语言只在 [docs/UNSUPPORTED_LANGS.md](docs/UNSUPPORTED_LANGS.md) 标注，**不建目录**。
- **Logo / Algol 68 / Modula-2 / Forth / Icon**：方言差异大，以源码 + README 为准，个别环境可能需微调。
- 跳过几乎无法在通用桌面运行的语言（如 RPG 仅限 IBM i）。
- 生成脚本（维护用）：`scripts/_gen_classic_langs.py`、`_gen_classic_langs_b.py`、`_gen_classic_langs_c.py`、`_gen_brainfuck_sokoban.py`
- **Esolang**：`brainfuckapp1/`（纯 BF）、`jsfuckapp1/`（脚本生成纯 JSFuck `try_move`）；禁止 Python 冒充其它 esolang 空壳。
