# netaotapp1 — .NET Native AOT 推箱子（教学）

> [English](README.md)


演示 **PublishAot**（Native AOT）：编译为**原生机器码**，目标机无需安装 .NET 运行时。  
**不强制在本仓库发布**；源码可直接阅读。

## 可选发布

```bash
cd netaotapp1
dotnet publish -c Release -r win-x64 --self-contained
# Linux: -r linux-x64
# macOS: -r osx-arm64 或 osx-x64
# 输出目录: bin/Release/net8.0/<rid>/publish/
```

开发调试（仍走 JIT，不必 AOT）：

```bash
dotnet run
```

键位：WASD 移动，z 撤销，r 重置，q 退出。

## 对照

| 目录 | 模式 |
|------|------|
| [`../csharpapp1`](../csharpapp1) | 常规托管 `dotnet` |
| [`../monoapp1`](../monoapp1) | Mono 运行时 |
| `netaotapp1`（本目录） | Native AOT 原生可执行文件 |

> AOT 限制：避免反射/动态程序集等；本示例仅用标准集合与控制台，适合 AOT。
