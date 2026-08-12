# netaotapp1 — .NET Native AOT Sokoban (teaching)

> [中文版](readme.zh.md)

**PublishAot**（Native AOT）： ** **， .NET 。 ** **.

## Run

```bash
cd netaotapp1
dotnet publish -c Release -r win-x64 --self-contained
# Linux: -r linux-x64
# macOS: -r osx-arm64 osx-x64
# : bin/Release/net8.0/<rid>/publish/
```

```bash
dotnet run
```

Controls: WASD move, z undo, r reset, q quit.
