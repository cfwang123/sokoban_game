# raylibapp1 — raylib 推箱子桌面 demo（教学）

C + [raylib](https://www.raylib.com/) 窗口。配色对齐 `html_app`。

```bash
cd raylibapp1
make
./sokoban
```

Windows 若 `pkg-config` 不可用，Makefile 默认链 `-lraylib -lopengl32 -lgdi32 -lwinmm`（需本机已装 raylib）。

键位：WASD / 方向键，Z 撤销，R 重置，Q 退出。
