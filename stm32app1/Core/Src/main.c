/**
 * STM32 推箱子教学 main（CubeMX 风格示意）。
 * 真机：CubeMX 生成工程后，把 game_core.* / mini_levels.h 加入工程，
 * 在 while(1) 中调用本逻辑；LCD/按键用 BSP。
 */
#include "game_core.h"

/* 桩：替换为 HAL 初始化 */
void SystemInit_Stub(void) {}
void board_draw(const GameCore *s);
int board_get_key(void); /* 0 none 1-4 dir 5 undo 6 reset */

void board_draw(const GameCore *s) {
  (void)s; /* 真机：SPI LCD 画格子；调试可 ITM/UART 打印 */
}

int board_get_key(void) {
  return 0; /* 真机：读 GPIO 矩阵 */
}

int main(void) {
  GameCore g;
  SystemInit_Stub();
  gc_load(&g, 0);
  board_draw(&g);
  for (;;) {
    int k = board_get_key();
    if (k == 1) gc_try_move(&g, 0, -1);
    else if (k == 2) gc_try_move(&g, 0, 1);
    else if (k == 3) gc_try_move(&g, -1, 0);
    else if (k == 4) gc_try_move(&g, 1, 0);
    else if (k == 5) gc_undo(&g);
    else if (k == 6) gc_load(&g, g.level);
    if (k) board_draw(&g);
    /* HAL_Delay(50); */
  }
}
