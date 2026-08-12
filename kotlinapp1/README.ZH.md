# kotlinapp1 — Kotlin 推箱子（教学）

> [English](readme.md)


标准库终端版。需要 Kotlin 编译器（`kotlinc`）或 IDEA。

```bash
cd kotlinapp1
kotlinc Game.kt Main.kt -include-runtime -d sokoban.jar
java -jar sokoban.jar
```

键位：WASD 移动，z 撤销，r 重置，q 退出。

对照：`androidapp1/`（Android Kotlin 完整版）。
