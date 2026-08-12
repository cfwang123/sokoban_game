# stm32app1 — STM32 推箱子（教学）

> [English](readme.md)


CubeMX 可合并的 `Core/Src` + `Core/Inc` 示意：裸机 `while(1)` 轮询。

```
Core/Inc/game_core.h  mini_levels.h
Core/Src/game_core.c  main.c
```

1. CubeMX 选芯片生成工程  
2. 添加上述文件到构建  
3. 实现 `board_draw` / `board_get_key` 对接 LCD 与按键  

本仓库不包含完整 HAL 库。
