# jetbrainsext1 — JetBrains IDE 插件推箱子（教学）

面向 **IntelliJ IDEA / Android Studio / WebStorm** 等（IntelliJ Platform）。

## 内容

| 文件 | 作用 |
|------|------|
| `META-INF/plugin.xml` | 插件清单：Tool Window + Tools 菜单 |
| `GameLogic.kt` | 推箱规则 |
| `SokobanPanel.kt` | 面板状态 |
| `SokobanToolWindowFactory.kt` | Tool Window 工厂（SDK 对接注释） |
| `SokobanConsole.kt` | **无 SDK 时控制台试玩** |

## 做成真插件

1. 安装 JDK 17+，用 IDEA 新建 **IDE Plugin** 工程，或本目录启用  
   `org.jetbrains.intellij` Gradle 插件并配置 `intellij.version`。  
2. 让 `SokobanToolWindowFactory` 实现 `ToolWindowFactory`，用 `JTextArea`/`JBLabel` 显示 `boardText`。  
3. `OpenSokobanAction` 继承 `AnAction`。  
4. Run Plugin 启动沙箱 IDE。  

## 无 SDK 试玩逻辑

```bash
cd jetbrainsext1
# 若已配 Kotlin 插件的 Gradle：
./gradlew runConsole
```

或在 IDE 中直接运行 `SokobanConsoleKt.main`。

## 对照

| VS Code | JetBrains |
|---------|-----------|
| package.json | plugin.xml |
| Webview | Tool Window (Swing/JCEF) |
| TypeScript | Kotlin |
