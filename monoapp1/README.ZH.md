# monoapp1 — Mono 推箱子（教学）

> [English](readme.md)


面向 **Mono**（`mcs` / `mono`）与经典 .NET Framework 风格 C# 的教学终端版。  
**不强制本仓库编译**；语法刻意偏保守，便于老版本 Mono。

## 可选本机运行

```bash
# Mono
mcs -out:sokoban.exe Program.cs Game.cs
mono sokoban.exe

# 或 Microsoft csc
# csc /out:sokoban.exe Program.cs Game.cs
# sokoban.exe
```

键位：WASD 移动，z 撤销，r 重置，q 退出。

## 对照

| 目录 | 运行时 |
|------|--------|
| `monoapp1`（本目录） | Mono / mcs |
| [`../csharpapp1`](../csharpapp1) | 现代 `dotnet` 行式 CLI |
| [`../netaotapp1`](../netaotapp1) | .NET Native AOT 发布 |

> Mono 与 .NET（Core）是不同实现；本示例演示「同一 C# 逻辑在 Mono 上跑」。
