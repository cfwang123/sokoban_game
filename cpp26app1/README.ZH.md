# cpp26app1 — C++03…C++26 语法展柜推箱子（可玩）

> [English](README.md)

与 `cppapp1/` 同一迷你关卡，但用 **`-std=c++26`** 把 **C++03 到 C++26** 各世代的代表性语法 / 标准库用法串进一局可玩的终端推箱子。对照：可读的 `cppapp1/`（C++17）、难读反例 `cpphardapp1/`。

## 编译运行

需要 GCC 15+（或 C++26 支持较完整的工具链）。**MinGW** 下 `<print>` 需链接 `libstdc++exp`：

```bash
cd cpp26app1
g++ -std=c++26 -O2 main.cpp -o sokoban -lstdc++exp
./sokoban
```

键位：WASD 移动，`z` 撤销，`r` 重置，`q` 退出。

## 文件

| 文件 | 说明 |
|------|------|
| `game.hpp` | 核心逻辑 + 语法 / 库展柜 |
| `main.cpp` | 终端循环、`#embed`、`print`、命令 `variant` |
| `level.min.txt` | 迷你关卡（经 C++26 `#embed` 嵌入二进制） |

## 按标准的特性表（非穷尽）

| 世代 | 本目录实际用到 |
|------|----------------|
| **C++03/98** | 模板、命名空间、STL（`vector`/`algorithm`/`string`）、`switch`、引用 |
| **C++11** | `auto`、`nullptr`、`constexpr`、范围 for、lambda、`enum class`、别名模板、`=default`/`=delete`、NSDMI、移动语义、`chrono`、`tuple`、UDL（`_cmd`）、CRTP 风格辅助 |
| **C++14** | 泛型 / 放宽 constexpr lambda、chrono UDL、变量模板 |
| **C++17** | `string_view`、`optional`、`variant`、结构化绑定、`if constexpr`、折叠表达式、嵌套命名空间、`[[nodiscard]]`、CTAD |
| **C++20** | concepts、ranges/views、`span`、`<=>`、`using enum`、指定初始化、`format`、`source_location`、协程（经 `generator`） |
| **C++23** | `print`/`println`、`expected`、`flat_set`、`generator`、deducing `this`、多维下标、`static operator()`、`auto(x)`、`zu` 后缀 |
| **C++26** | `#embed`、包索引 `Ts...[N]`、占位符 `_`、`= delete("reason")`、结构化绑定旁属性、结构化绑定作 `if` 条件、`variant::visit` 成员函数 |

未强行塞入 modules / reflection / contracts 等仍依赖更新工具链的特性；上表均为在 GCC 15 `-std=c++26` 下**已编译可运行**的用法。
