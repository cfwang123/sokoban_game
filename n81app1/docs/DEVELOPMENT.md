# Nokia N81 / Java ME 开发速查

## 平台是什么？

| 项 | 说明 |
|----|------|
| 机型 | Nokia N81（2007） |
| 系统 | Symbian OS 9.2 · Series 60 3rd Edition Feature Pack 1 |
| Java | **Java ME**：CLDC 1.1 + **MIDP 2.0** |
| 输入 | 数字键盘 + 四向导航键 + 左右软键（**无电容触屏**） |
| 屏幕 | 约 240×320 |

本目录演示的是 **MIDlet** 应用（`.jar` + `.jad`），不是 Android APK，也不是 Symbian 原生 C++。

## 和现代平台对照

| 概念 | Java ME (本工程) | Android | iOS |
|------|------------------|---------|-----|
| 入口 | `MIDlet` 子类 | `Activity` | `@main App` |
| 生命周期 | startApp / pauseApp / destroyApp | onResume / onPause… | scene phase |
| 全屏绘制 | `Canvas.paint(Graphics)` | `View.onDraw` | SwiftUI `Canvas` |
| 按键 | `keyPressed` + `getGameAction` | KeyEvent / 虚拟键 | 手势 / 键盘 |
| 本地小存储 | **RMS** `RecordStore` | SharedPreferences | UserDefaults |
| 列表 UI | `List` / `Form` / `Alert` | RecyclerView… | List / Alert |
| 构建产物 | `MIDlet.jar` + `.jad` | APK/AAB | IPA |

## 生命周期（必记）

```text
构造 MIDlet
    → startApp()     // 显示 Canvas / Form
    → pauseApp()     // 来电、切走：停动画/声音
    → startApp()     // 回到前台
    → destroyApp()   // 退出
```

## 按键约定（N81 / S60）

| 键 | 本演示用途 |
|----|------------|
| 方向键 / 2 4 6 8 | 移动 |
| 左软键 (-6) / 7 | 撤销 |
| 右软键 (-7) | 菜单；通关后下一关 |
| 0 | 重置 |
| 1 / 3 | 上一关 / 下一关 |
| * | 查看或停止答案 |
| # | 帮助 |

不同机型软键 keyCode 可能不同；量产应用应做机型适配或使用 `Command` 绑定软键。

## 源码映射

| 文件 | 职责 |
|------|------|
| `SokobanMIDlet.java` | 入口、菜单、Alert |
| `GameCanvas.java` | 绘制、按键、答案线程 |
| `GameState.java` | 推箱规则、撤销 |
| `Pathfinding.java` | BFS（菜单「演示寻路」） |
| `LevelsData.java` | 关卡常量数组 |
| `Prefs.java` | RMS 记关卡 |

## 如何真机/模拟器运行（可选，需工具链）

1. 安装 **Java ME SDK** 或 **Sun Wireless Toolkit / WTK**，或 Nokia S60 SDK + Carbide/旧版工具。  
2. 将 `src` 编成 class（目标 bootclasspath 为 MIDP/CLDC）。  
3. 打包 `jar`，`MANIFEST.MF` 含 `MIDlet-1` 等属性（见 `bin/MANIFEST.MF`）。  
4. 写 `.jad` 描述 jar URL 与大小，传到手机安装，或用模拟器打开。  

> 本仓库**不要求**配置上述工具链；源码与文档用于理解结构。

## 设计取舍（教学向）

- **无 JSON 库**：关卡生成进 `LevelsData` 字符串数组。  
- **无 HashSet**：`boolean[]` 网格。  
- **无触屏点地**：BFS 在菜单「演示BFS寻路」中调用。  
- **演示关卡子集**：约 35 关，减小 jar 体积；完整关卡可用脚本从 `levels.json` 再生成。  
