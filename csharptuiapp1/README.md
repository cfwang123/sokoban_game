# csharptuiapp1 — C# TUI 推箱子（教学）

纯控制台 **TUI 循环**（ANSI 清屏 + 彩色字符 + 立即按键），**零第三方包**。  
**不要求在本仓库内编译**。

可选：

```bash
cd csharptuiapp1
dotnet run
```

键位：WASD / 方向键，Z 撤销，R 重置，Q/Esc 退出。

与行式 CLI [`../csharpapp1`](../csharpapp1) 的区别：本版全屏刷新、按键即时响应（更接近 TUI 框架用法）；需要 Spectre.Console / Terminal.Gui 时可在此基础上替换绘制层。
