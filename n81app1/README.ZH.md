# 推箱子 Nokia N81 版 (n81app1) — 教学演示

> [English](README.md)


面向 **Nokia N81**（Symbian S60 3rd Edition FP1）的 **Java ME / MIDP 2.0** 推箱子源码，用于**演示功能机 Java 应用如何组织与开发**。

[更新日志](CHANGELOG.md) · [开发速查](docs/DEVELOPMENT.md)

**当前版本：1.0.0**

> **说明**  
> - 提供完整、可读的 J2ME 源码与清单示例，**不要求在本仓库内完成编译与打包**。  
> - 玩法对齐 [`html_app`](../html_app) / [`androidapp1`](../androidapp1)，并按 N81 **无触屏、数字键盘** 做了交互裁剪。  
> - 关卡为演示子集（约 35 关，见 `LevelsData.java`）。

---

## 1. 为什么是 Java ME？

2000 年代诺基亚 S60 手机除了 Symbian C++，还广泛支持 **MIDlet**（Java ME）：

- 一套 jar 可在多款支持 MIDP 2.0 的机型上运行（仍需适配分辨率与键码）。  
- 开发入口低：会 Java SE 语法即可上手（API 面更小）。  
- 发布形态：`.jad`（描述）+ `.jar`（字节码与资源）。

N81 即属于这一代：**CLDC 1.1 + MIDP 2.0**。

---

## 2. 工程结构

```
n81app1/
├── README.ZH.md
├── README.md
├── CHANGELOG.md
├── .gitignore
├── bin/
│   ├── MANIFEST.MF      # 打入 jar 的清单模板
│   └── Sokoban.jad      # 安装描述模板（Jar-Size 打包后需改）
├── docs/DEVELOPMENT.md  # 生命周期 / 按键 / 对照表
├── res/levels_demo.json # 导出用的关卡子集（生成 Java 的源）
└── src/com/whj/sokoban/
    ├── SokobanMIDlet.java   # @入口 MIDlet
    ├── GameCanvas.java      # 画面 + 按键
    ├── GameState.java       # 规则
    ├── Pathfinding.java     # BFS
    ├── LevelsData.java      # 关卡常量
    ├── Prefs.java           # RMS 存档
    └── Direction.java
```

### 推荐阅读顺序

1. `docs/DEVELOPMENT.md` — 平台背景  
2. `SokobanMIDlet.java` — 生命周期与菜单  
3. `GameCanvas.java` — `paint` / `keyPressed`  
4. `GameState.java` / `Pathfinding.java` — 与 Android 相同的规则思路  

---

## 3. 功能一览

| 能力 | N81 上的做法 |
|------|----------------|
| 移动 / 推箱 | 方向键或 2/4/6/8 |
| 撤销 | 左软键或 7（只撤推箱步） |
| 重置 | 0 |
| 换关 | 1 / 3 或菜单 |
| 查看答案 | `*` 回放 / 停止（有 solution 的关） |
| 帮助 | `#` 或菜单 |
| 点地寻路 | **无触屏** → 菜单「演示BFS寻路」 |
| 记关卡 | RMS `RecordStore` |

---

## 4. 与 androidapp1 / iosapp1 对照

| 主题 | n81app1 | androidapp1 | iosapp1 |
|------|---------|-------------|---------|
| 语言 | Java ME | Kotlin | Swift |
| UI | `Canvas` + `List` | View + XML | SwiftUI |
| 存储 | RMS | SharedPreferences | UserDefaults |
| 关卡 | `LevelsData` 数组 | assets JSON | Bundle JSON |
| 构建 | jar/jad（需 WTK 等） | Gradle | Xcode |

---

## 5. 可选：重新生成关卡子集

```bat
cd n81app1
python -X utf8 tools\gen_levels.py
```

（读取 `res/levels_demo.json`，生成 `src/.../LevelsData.java`。）

若要从完整 `levels.json` 重采样，可先写 JSON 子集到 `res/levels_demo.json` 再运行脚本。

---

## 6. 可选：打包思路（不在本仓库执行）

```text
javac -bootclasspath <midp-classes> -source 1.3 -target 1.3 -d classes src/com/whj/sokoban/*.java
jar cvfm Sokoban.jar bin/MANIFEST.MF -C classes .
# 填写 jad 中 MIDlet-Jar-Size 后安装到模拟器或 N81
```

具体 bootclasspath 取决于本机 Java ME SDK 路径，**请勿把本机绝对路径写进仓库**。

---

## 参考

- 玩法：[`../html_app`](../html_app)  
- Android：[`../androidapp1`](../androidapp1)  
- iOS 教学：[`../iosapp1`](../iosapp1)  
- [MIDP 2.0 规范概览](https://www.oracle.com/java/technologies/javameoverview.html)（历史文档）  
