# esp32app1 — ESP32 推箱子（教学）

> [English](readme.md)


ESP-IDF 风格：`app_main` + FreeRTOS 轮询 + `game_core` + `mini_levels.h`。  
显示/按键为 **weak stub**，接 OLED/GPIO 时提供强符号覆盖。

```bash
# 需安装 ESP-IDF
cd esp32app1
idf.py set-target esp32
idf.py build flash monitor
```

本仓库不强制 IDF 环境。
