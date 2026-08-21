# 推箱子 · 步步高文曲星 (wqxapp1) — 教学工程

> [English](README.md)


在 **步步高文曲星** 类电子词典上运行的推箱子 **C 语言工程演示**（分层 HAL + 玩法核心）。

[更新日志](CHANGELOG.md) · [开发速查](docs/DEVELOPMENT.md)

**当前版本：1.0.0**

> **说明**  
> - 完整可阅读源码与工程骨架，**不要求在本仓库编出真机固件**。  
> - 文曲星历代 SDK/分辨率不统一，故用 `wqx/wqx_api.h` **抽象机型接口**，真机时再对接厂商库。  
> - 玩法对齐 `html_app` / `androidapp1` / `n81app1`（推箱规则、撤销、答案回放、记关卡）。  
> - 关卡为演示子集（约 20 关），见 `levels_data.c`。

---

## 1. 为什么是 C + HAL？

电子词典时代常见做法：

| 点 | 说明 |
|----|------|
| 语言 | C（RAM/ROM 小，工具链以 C 为主） |
| 显示 | 直接写显存/画点矩形，少见完整 GUI 框架 |
| 输入 | 扫描键矩阵，主循环轮询 |
| 资源 | 关卡、字模编译进程序，少用大文件系统 |

本工程按该模式拆分，便于对照 Android/Java ME/HTML 移植。

---

## 2. 目录结构

```
wqxapp1/
├── README.ZH.md
├── README.md
├── CHANGELOG.md
├── Makefile              # 教学：list / 可选 host 语法检查
├── docs/DEVELOPMENT.md
├── include/
│   ├── wqx/wqx_api.h     # 机型 HAL 契约（核心教学文件）
│   ├── game.h
│   ├── pathfinding.h
│   ├── ui.h
│   ├── app.h
│   └── levels_data.h
├── src/
│   ├── main.c            # 入口
│   ├── app.c             # 主循环 / 键位 / 答案回放
│   ├── game.c            # 推箱状态机
│   ├── pathfinding.c     # BFS
│   ├── ui.c              # 状态栏 + 棋盘绘制
│   ├── levels_data.c     # 嵌入关卡
│   └── wqx_hal_stub.c    # 无 SDK 时的桩实现
├── res/levels_demo.json  # 生成关卡用
└── tools/gen_levels.py
```

### 阅读顺序

1. `include/wqx/wqx_api.h`  
2. `src/app.c`  
3. `src/game.c` + `src/ui.c`  
4. `src/wqx_hal_stub.c`  

---

## 3. 功能

| 能力 | 实现 |
|------|------|
| 移动推箱 | 方向键逻辑键 |
| 撤销 | 仅撤销推箱步 |
| 重置 / 换关 | RESET / PREV / NEXT |
| 答案回放 | 有 solution 时逐步播放 |
| 记关卡 | `wqx_nv_*` |
| 点地寻路 | 无触屏 → MENU 键演示 BFS 走到较远空地 |

逻辑分辨率演示值：**240×160** 灰阶（可按机型修改）。

---

## 4. 与其它目录对照

| 目录 | 平台 |
|------|------|
| `html_app` | 浏览器 2D |
| `androidapp1` | Android |
| `iosapp1` | iOS 教学 |
| `n81app1` | Nokia N81 Java ME |
| **`wqxapp1`** | **文曲星电子词典 C** |
| `c_app` | PC 控制台 |

---

## 5. 可选命令

```bat
cd wqxapp1
make help
make list
```

若本机有 `gcc`：

```bat
make host-syntax
```

仅做语法检查，**不是**文曲星固件。

重新生成关卡子集：

```bat
python -X utf8 tools\gen_levels.py
```

---

## 6. 真机移植（概念步骤）

1. 取得对应机型开发文档/SDK（因机型而异，本仓库不提供）。  
2. 实现 `wqx_api.h` → `wqx_hal_device.c`，替换 stub。  
3. 用厂商规定的编译器与打包格式生成安装包。  
4. 适配分辨率、键值、中文字库。  

---

## 参考

- 玩法：[`../html_app`](../html_app)  
- 功能机 Java 对照：[`../n81app1`](../n81app1)  
- PC 控制台 C：[`../c_app`](../c_app)  
