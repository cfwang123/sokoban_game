# unityapp1 — Unity 推箱子（教学）

> [English](README.md)


C# 逻辑脚本 + `GameController`（Gizmos/OnGUI 示意）。**不包含** `Library/`、完整 `.unity` 场景二进制，避免仓库膨胀。

## 在 Unity 中打开

1. Unity Hub → 新建 **2D** 或 **3D** 工程（2021 LTS+ 即可）。  
2. 将本目录 `Assets/Scripts` 拷入工程 `Assets/`。  
3. Hierarchy → Create Empty → 命名 `Game` → Add Component `GameController`。  
4. 按 Play：Scene 视图看 Gizmos，Game 视图看左上角步数。  

## 结构

```
Assets/Scripts/
  GameController.cs
  Game/GameState.cs
  Game/Direction.cs
```

## 扩展

- 用 Tilemap / Sprite 替换 Gizmos。  
- 从 `TextAsset` 加载 `levels.json`。  
- 导出 Android/WebGL 构建。  
