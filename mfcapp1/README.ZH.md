# mfcapp1 — MFC 推箱子（教学）

> [English](README.md)


示意 **MFC Document/View** 分层的教学源码，**不要求在本仓库内编译**。

## 结构

| 文件 | 说明 |
|------|------|
| `SokobanDoc.h/.cpp` | 文档：关卡状态、移动/撤销 |
| `SokobanView.h/.cpp` | 视图：GDI 绘制、键盘 |
| （完整工程） | 用 VS「MFC 应用程序」向导新建后，把上述类并入即可 |

## 如何在本机试跑（可选）

1. Visual Studio → 新建 **MFC 应用**（单文档 SDI）  
2. 将 `CSokobanDoc` / `CSokobanView` 逻辑并入向导生成的 Doc/View  
3. 启动对象与消息映射按 MFC 惯例连接  
4. F5 运行  

本目录只放**核心教学代码**，不附带完整 `.vcxproj` / 预编译头，避免绑定特定 VS 版本。

## 键位

WASD / 方向键，Z 撤销，R 重置，Esc/Q 退出。

对照：纯 Win32 [`../win32app1`](../win32app1)
