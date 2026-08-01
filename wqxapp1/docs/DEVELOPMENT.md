# 步步高文曲星（WQX）推箱子 — 开发速查

## 1. 目标设备是什么？

| 项 | 说明 |
|----|------|
| 品牌/产品 | 步步高 **文曲星** 电子词典（历代 PC / TC / E 等机型） |
| 形态 | 掌上词典：点阵或少灰阶 LCD + 实体键盘，RAM/Flash 紧张 |
| 应用形态 | 厂商/社区 C 工具链编译的本地小程序（非 Android APK） |
| 本仓库定位 | **教学演示**：HAL 抽象 + 完整玩法源码，**不绑定已停产 SDK，不要求编译出固件** |

> 各代文曲星 API 并不统一。本工程用 `wqx/wqx_api.h` 描述「写小游戏时真正需要的能力」，真机时再映射到具体 SDK。

## 2. 和其它移植对照

| 主题 | wqxapp1（文曲星） | n81app1（N81） | androidapp1 |
|------|-------------------|----------------|-------------|
| 语言 | C99 | Java ME | Kotlin |
| 显示 | 点阵/灰阶 `wqx_fill_*` | `Canvas.paint` | 自定义 View |
| 输入 | 键扫描轮询 | `keyPressed` | 触屏 + 虚拟键 |
| 存档 | NV / Flash 小槽 | RMS | SharedPreferences |
| 关卡 | 编译进 `levels_data.c` | `LevelsData.java` | assets JSON |
| 主循环 | `app_run` while+delay | 系统事件 | Activity 生命周期 |

## 3. 推荐工程分层

```
应用层   app.c / ui.c     状态机、绘制布局、键位逻辑
玩法层   game.c / pathfinding.c / levels_data.c
HAL 层   wqx_api.h + wqx_hal_*.c
```

原则（电子词典开发通用）：

1. **玩法与机型 API 分离** — `game.c` 不 include 厂商头文件。  
2. **关卡进固件** — 避免运行时解析大 JSON。  
3. **ASCII 状态栏** — 中文需字库；演示用英文/数字减少依赖。  
4. **轮询主循环** — 许多词典 SDK 无复杂事件框架，用 `poll + delay` 即可。

## 4. 键位映射（演示约定）

| 逻辑键 | 建议物理键 | 功能 |
|--------|------------|------|
| UP/DOWN/LEFT/RIGHT | 方向键 | 移动/推箱 |
| UNDO | 返回 / Z | 撤销推箱步 |
| RESET | R / 清除 | 重置本关 |
| PREV/NEXT | 翻页键 | 上一关/下一关 |
| ANSWER | A / 功能键 | 答案回放 |
| MENU | 菜单 | 本演示：BFS 自动走远格 |
| ESC 长按 | 退出 | 退回系统 |

## 5. 真机移植清单

1. 实现 `wqx_api.h` 全部函数（显示缓冲、键矩阵、延时、NV）。  
2. 确认 LCD 分辨率，改 `WQX_LCD_W/H` 或做缩放。  
3. 若有中文字库，替换 `wqx_draw_text` 与 UI 字符串。  
4. 用厂商打包工具生成可安装程序（格式因机型而异，本仓库不模拟具体容器）。  
5. 控制体积：减少关卡、去掉答案字符串、压缩字模。

## 6. 源码阅读顺序

1. `include/wqx/wqx_api.h` — 设备能力契约  
2. `src/main.c` → `src/app.c` — 入口与主循环  
3. `src/game.c` — 推箱规则  
4. `src/ui.c` — 如何把格子画到 240x160  
5. `src/wqx_hal_stub.c` — 无 SDK 时的桩  
