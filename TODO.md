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
| `aplapp1/` | APL（+ Python 可运行驱动） | ✅ |
| `factorapp1/` | Factor（+ Python 可运行驱动） | ✅ |

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
| `awkapp1/` | AWK | ✅ |
| `sqlapp1/` | SQL / SQLite | ✅ |
| `cppapp1/` | C++ | ✅ |
| `groovyapp1/` | Groovy | ✅ |
| `vapp1/` | V | ✅ |
| `odinapp1/` | Odin | ✅ |

## 既有（本清单不重复）

Python / PHP / Lua / Node.js / Ruby / Java / C# / Kotlin / Perl / R / Haskell / Rust / Go / Zig 及桌面/主机/扩展等，见根目录 README。

## 说明

- 多数为教学演示，不强制本机安装对应工具链。
- **APL / Factor**：仓库内以 Python 驱动保证可玩；同目录保留原生语言骨架供对照。
- **Logo / Algol 68 / Modula-2 / Forth / Icon**：方言差异大，以源码 + README 为准，个别环境可能需微调。
- 跳过几乎无法在通用桌面运行的语言（如 RPG 仅限 IBM i）。
- 生成脚本（维护用）：`scripts/_gen_classic_langs.py`、`_gen_classic_langs_b.py`、`_gen_classic_langs_c.py`
