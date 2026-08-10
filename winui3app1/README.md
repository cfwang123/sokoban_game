# winui3app1 — WinUI 3 推箱子（教学）

Windows **WinUI 3 / Windows App SDK** 教学源码，**不要求在本仓库内编译**。

本目录聚焦 **Game + MainWindow**，不附带完整打包清单与 `Platforms` 样板（随 Windows App SDK 版本变化）。

## 核心文件

| 文件 | 说明 |
|------|------|
| `Game.cs` | 玩法逻辑 |
| `MainWindow.xaml` / `.xaml.cs` | 窗口 UI、键盘与按钮 |
| `App.xaml` / `App.xaml.cs` | 应用入口示意 |

## 可选本机运行

1. Visual Studio 2022+，安装 **.NET 桌面开发** + **Windows App SDK**  
2. `dotnet new winui -n SokobanWinUIRun`（或 VS「空白应用 包装 (WinUI 3)」）  
3. 并入本目录 `Game.cs`、`MainWindow.*`、`App.*` 逻辑  
4. F5 运行  

键位：WASD / 方向键，Z 撤销，R 重置；亦可用按钮。

对照：WPF [`../wpfapp1`](../wpfapp1) · MAUI [`../mauiapp1`](../mauiapp1) · WinForms [`../winformsapp1`](../winformsapp1)
