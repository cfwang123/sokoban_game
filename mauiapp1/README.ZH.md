# mauiapp1 — .NET MAUI 推箱子（教学）

> [English](README.md)


跨平台 **.NET MAUI** 教学源码（Android / iOS / Windows / macOS），**不要求在本仓库内编译**。

本目录提供 **玩法 + MainPage UI 核心文件**，不捆绑完整 `Platforms/*` 与签名配置（随 VS/工作负载版本变化大）。

## 核心文件

| 文件 | 说明 |
|------|------|
| `Game.cs` | 玩法逻辑 |
| `MainPage.xaml` / `.xaml.cs` | 界面与按钮 |
| `App.xaml` / `MauiProgram.cs` | 应用入口示意 |

## 可选本机运行

1. 安装 [.NET MAUI 工作负载](https://learn.microsoft.com/dotnet/maui/get-started/installation)  
2. `dotnet new maui -n SokobanMauiRun`  
3. 将本目录 `Game.cs`、`MainPage.*`、`App.*`、`MauiProgram.cs` 逻辑并入工程  
4. `dotnet build -t:Run -f net8.0-windows10.0.19041.0`（或 VS 选目标设备 F5）

键位/按钮：WASD 方向按钮，Z 撤销，R 重置。

对照：WinUI 3 [`../winui3app1`](../winui3app1) · Avalonia [`../avaloniaapp1`](../avaloniaapp1) · 纯 CLI [`../csharpapp1`](../csharpapp1)
