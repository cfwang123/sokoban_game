# modula2app1 — Modula-2 推箱子（教学）

需要 [GNU Modula-2](https://www.nongnu.org/gm2/)（`gm2`，GCC 插件）。API 按 GM2 方言，其它编译器可能需微调。

```bash
cd modula2app1
gm2 -O2 -I. Main.mod -o sokoban
./sokoban
```

键位：WASD 移动，z 撤销，r 重置，q 退出。
