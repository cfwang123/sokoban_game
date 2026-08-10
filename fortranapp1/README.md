# fortranapp1 — Fortran 推箱子（教学）

需要 [gfortran](https://gcc.gnu.org/fortran/)（GCC Fortran）。

```bash
cd fortranapp1
gfortran -O2 game.f90 main.f90 -o sokoban
./sokoban
# Windows:
# sokoban.exe
```

键位：WASD 移动，z 撤销，r 重置，q 退出。
