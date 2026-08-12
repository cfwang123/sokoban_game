# powershellapp1 — PowerShell 推箱子（教学）

> [English](readme.md)


纯 **PowerShell** 脚本（Windows PowerShell 5.1+ 或 PowerShell 7 `pwsh`）。

## 运行

```powershell
cd powershellapp1
# PowerShell 7
pwsh -NoProfile -File main.ps1
# Windows PowerShell（若执行策略拦截）
powershell -NoProfile -ExecutionPolicy Bypass -File main.ps1
```

键位：WASD 移动，z 撤销，r 重置，q 退出。

## 文件

| 文件 | 说明 |
|------|------|
| `Game.ps1` | 核心逻辑 |
| `main.ps1` | 主循环 |

## 对照

| 目录 | 环境 |
|------|------|
| [`../cmdapp1`](../cmdapp1) | Windows CMD / 批处理 |
| `powershellapp1`（本目录） | PowerShell |
| [`../bashapp1`](../bashapp1) | Bash |
