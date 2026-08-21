# cpphardapp1 — 故意难读的 C++ 推箱子

> [English](README.md)

玩法与其它终端版相同，但实现刻意堆满 **难读 C++ 语法**（宏、`##` 拼接标识符、CRTP、成员函数指针表、`std::variant` + 重载集、逗号运算符链、嵌套三元、`bitset` 编解码方向……）。

这是教学用的 **反例 / 语法展柜**，不是推荐写法。日常请看 `cppapp1/`（可读 C++17）或 `cpp26app1/`（C++03～C++26 语法展柜）。

## 编译运行

```bash
cd cpphardapp1
g++ -std=c++17 -O2 main.cpp -o sokoban
./sokoban
```

键位：WASD 移动，`z` 撤销，`r` 重置，`q` 退出。

## 文件

| 文件 | 说明 |
|------|------|
| `game.hpp` | 难读核心（`_::Game`、宏、模板） |
| `main.cpp` | 难读输入循环（`variant` / `Ov` / 管道） |
