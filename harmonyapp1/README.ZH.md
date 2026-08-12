# harmonyapp1 — HarmonyOS 推箱子（教学）

> [English](readme.md)


ArkTS 状态机 + 声明式 UI 示意。**用 DevEco Studio 新建工程后拷入 `entry/src/main/ets`。**

本仓库不包含完整 `oh-package.json5` / 签名配置（随本机 SDK 生成）。

## 结构

```
entry/src/main/ets/
  game/GameState.ets
  pages/Index.ets
```

## 对照

| Harmony | Android |
|---------|---------|
| `@Entry @Component` | Activity + Compose/View |
| `@State` | LiveData / 手动 setState |
| ArkTS Set | Kotlin Set |
