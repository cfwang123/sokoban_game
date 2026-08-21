# blazorapp1 — Blazor WebAssembly 推箱子（教学）

> [English](README.md)


C# **Blazor WASM** 组件教学源码，**不强制在本仓库编译**。

## 结构

| 路径 | 说明 |
|------|------|
| `Game.cs` | 玩法核心 |
| `Components/SokobanBoard.razor` | 棋盘 + 键盘/按钮 |
| `Components/Pages/Home.razor` | 路由 `/` |
| `Program.cs` / `wwwroot/` | WASM 宿主 |

## 可选本机运行

```bash
cd blazorapp1
dotnet run
# 浏览器打开输出的 https/http 地址
```

键位：WASD / 方向键，Z 撤销，R 重置。

对照：React [`../reactapp1`](../reactapp1) · WinForms [`../winformsapp1`](../winformsapp1)

> Blazor 必须经 .NET 构建发布；与 CDN React/Vue 不同，无法双击 HTML 即玩。源码可直接阅读 `.razor` 组件写法。
