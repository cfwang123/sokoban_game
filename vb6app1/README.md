# vb6app1 — Visual Basic 6.0 推箱子（教学）

经典 **VB6** Standard EXE（`Sub Main`，无窗体）。

## 需要

- Visual Basic 6.0 IDE（或兼容环境）
- Windows；`Scripting.Dictionary`（`CreateObject`，一般无需勾引用）

## 打开与运行

1. 用 VB6 打开 `sokoban.vbp`
2. **工程 → 属性 → 通用 → 启动对象** 选 **`Sub Main`**
3. **F5** 运行，或 **文件 → 生成 sokoban.exe…**

交互：地图与状态显示在 **InputBox** 提示里，输入 `w`/`a`/`s`/`d`/`z`/`r`/`q`。

键位：WASD 移动，z 撤销，r 重置，q 退出。

## 文件

| 文件 | 说明 |
|------|------|
| `Game.bas` | 核心逻辑（Dictionary 存墙/箱/目标） |
| `Main.bas` | `Sub Main` 入口 |
| `sokoban.vbp` | VB6 工程文件 |

## 对照

| 目录 | 语言 |
|------|------|
| [`../basicapp1`](../basicapp1) | FreeBASIC |
| [`../vbapp1`](../vbapp1) | VB.NET（`dotnet run`） |
| [`../vbaapp1`](../vbaapp1) | Excel VBA 宏 |
| `vb6app1`（本目录） | Visual Basic 6.0 |

## 说明

- **不要求在本仓库内编译**；多数环境已无 VB6。
- 源码为纯文本 `.bas` / `.vbp`，可直接阅读逻辑。
- 与 `vbaapp1` 逻辑几乎同构；VB6 为独立 EXE，VBA 挂在 Office 宿主上。
