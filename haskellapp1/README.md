# haskellapp1 — Haskell 推箱子（教学）

需要 [GHC](https://www.haskell.org/ghc/)。纯标准库 + `containers`（GHC 自带）。

```bash
cd haskellapp1
ghc -O Main.hs Game.hs -o sokoban
./sokoban
# Windows:
# sokoban.exe
```

键位：WASD 移动，z 撤销，r 重置，q 退出。
