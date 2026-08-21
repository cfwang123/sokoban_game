# sdlapp1 — SDL2 推箱子桌面 demo（教学）

> [English](README.md)


轻量 C + SDL2 窗口。配色对齐 `html_app`。同思路可用 [SFML](https://www.sfml-dev.org/) 重写（C++ `sf::RenderWindow`）。

## 依赖

- SDL2 开发库（Windows: MSYS2 `mingw-w64-x86_64-SDL2`，或官方开发包）

```bash
cd sdlapp1
make
./sokoban
```

Windows（已配好 `pkg-config` / 库路径时）：

```bat
gcc -O2 -o sokoban.exe main.c -lSDL2
```

## 键位

| 键 | 功能 |
|----|------|
| 方向键 / WASD | 移动 |
| Z | 撤销推箱 |
| R | 重置 |
| Q / Esc | 退出 |
