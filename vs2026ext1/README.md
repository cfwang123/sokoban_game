# vs2026ext1 — Visual Studio 扩展推箱子（教学）

面向 **Visual Studio 2022 / 预览版与后续 VS（俗称 2026 一代）** 的扩展开发示意：

- `GameLogic.cs` — 推箱规则  
- `SokobanToolWindow.cs` — Tool Window / Package 注册说明  
- `Program.cs` — **无 VSSDK 时**用控制台验证逻辑  

## 在 Visual Studio 中做成真扩展

1. 安装工作负载：**Visual Studio 扩展开发**（含 VSSDK）。  
2. 新建项目：**VSIX Project**（C#）。  
3. 目标版本勾选 VS 2022 及更新（随安装的 VS 版本变化）。  
4. 添加 **Tool Window** 项模板，把 `GameLogic` 接到 WPF `UserControl`。  
5. VSCT 增加菜单：视图 → 其它窗口 → 推箱子。  
6. F5 启动**实验实例**调试；发布为 `.vsix`。  

> 本目录 **SDK 风格 csproj 仅作阅读/控制台试玩**，完整 VSIX 清单随本机 VS 模板生成，避免绑定某一预览版号。

## 控制台试玩（可选）

```bash
cd vs2026ext1
dotnet run
```

（需 .NET SDK；`net48` 在 Windows 上通常可用。）

## 与 vscodeext1 对照

| | VS Code | Visual Studio |
|--|---------|----------------|
| 清单 | `package.json` | VSIX + VSCT |
| UI | Webview HTML | WPF Tool Window |
| 语言 | TypeScript | C# |
| 调试 | 扩展开发主机 | Experimental Instance |
