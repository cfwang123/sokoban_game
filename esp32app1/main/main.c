/**
 * ESP32 推箱子教学入口（ESP-IDF）。
 * 显示/按键通过弱符号桩；真机接 SSD1306 / 按键 GPIO。
 */
#include "game_core.h"
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* 弱实现：无硬件时 UART 打印 ASCII */
void __attribute__((weak)) board_init(void) {
  printf("[esp32] board_init stub\n");
}
void __attribute__((weak)) board_draw(const GameCore *s) {
  int y, x;
  printf("\nLV%d moves=%d%s\n", s->level + 1, s->moves, s->won ? " WIN" : "");
  for (y = 0; y < s->h; y++) {
    for (x = 0; x < s->w; x++) {
      int i = gc_idx(s, x, y);
      char c = ' ';
      if (s->px == x && s->py == y) c = s->goals[i] ? '+' : '@';
      else if (s->boxes[i]) c = s->goals[i] ? '*' : '$';
      else if (s->walls[i]) c = '#';
      else if (s->goals[i]) c = '.';
      putchar(c);
    }
    putchar('\n');
  }
}
/* 返回 0 无键；1上2下3左4右5撤销6重置 */
int __attribute__((weak)) board_poll_key(void) { return 0; }

void app_main(void) {
  GameCore g;
  board_init();
  gc_load(&g, 0);
  board_draw(&g);
  for (;;) {
    int k = board_poll_key();
    if (k == 1) gc_try_move(&g, 0, -1);
    else if (k == 2) gc_try_move(&g, 0, 1);
    else if (k == 3) gc_try_move(&g, -1, 0);
    else if (k == 4) gc_try_move(&g, 1, 0);
    else if (k == 5) gc_undo(&g);
    else if (k == 6) gc_load(&g, g.level);
    if (k) board_draw(&g);
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}
