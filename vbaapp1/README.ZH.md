# vbaapp1 — VBA 推箱子（教学）

> [English](readme.md)


面向 **Excel / Office VBA**（也可用于 Word/Access 等支持 VBA 的宿主）。  
与 [`../vbapp1`](../vbapp1)（VB.NET 终端）对照学习。

## 文件

| 文件 | 说明 |
|------|------|
| `Game.bas` | 核心逻辑（Dictionary 存墙/箱/目标） |
| `Main.bas` | 宏 `SokobanMain`：InputBox 操作 |

## 在 Excel 中运行

1. 启用「开发工具」选项卡  
2. **Alt+F11** 打开 VBA 编辑器  
3. **文件 → 导入文件**，依次导入 `Game.bas`、`Main.bas`  
4. **工具 → 引用** 中确认可使用 `Scripting.Dictionary`（通常 `CreateObject` 即可，无需勾引用）  
5. **Alt+F8** → 运行宏 **`SokobanMain`**

键位（在 InputBox 中输入）：WASD 移动，z 撤销，r 重置，q 退出。

可选：在 VBA 立即窗口调用 `DrawToSheet state` 把地图画到活动工作表（需先有 `GameState` 变量；见 `Main.bas` 中过程）。

## 说明

- VBA **不是**独立可执行程序，必须挂在 Office 等宿主上。  
- 本实现用 `MsgBox` / `InputBox` 做简易 UI，便于教学，不依赖窗体。  
- 需要允许运行宏（文件可存为 `.xlsm` 后导入模块）。

对照：

- VB.NET 终端：[`../vbapp1`](../vbapp1)
- VB6：[`../vb6app1`](../vb6app1)
- FreeBASIC：[`../basicapp1`](../basicapp1)
