/**
 * Game Boy 推箱子主循环（教学）。
 * 编译目标：GBDK-2020 或 RGBDS 汇编工程中链入 game_core。
 * 本仓库不强制产出 .gb。
 */
#include "game_core.h"
#include "gb_hw.h"

#include <stdio.h>

static void draw(const GameCore *s) {
  int cell, ox, oy, x, y;
  char line[24];
  gb_cls(0);
  /* 顶栏用字符格 */
  sprintf(line, "L%d M%d", s->level + 1, s->moves);
  gb_print(0, 0, line);

  cell = GB_LCD_W / (s->w > 0 ? s->w : 1);
  if ((GB_LCD_H - 16) / (s->h > 0 ? s->h : 1) < cell)
    cell = (GB_LCD_H - 16) / (s->h > 0 ? s->h : 1);
  if (cell < 4) cell = 4;
  ox = (GB_LCD_W - cell * s->w) / 2;
  oy = 16 + ((GB_LCD_H - 16) - cell * s->h) / 2;

  for (y = 0; y < s->h; y++) {
    for (x = 0; x < s->w; x++) {
      int i = gc_idx(s, x, y);
      unsigned char sh = s->walls[i] ? 3 : 1;
      if (s->boxes[i]) sh = s->goals[i] ? 2 : 3;
      else if (s->goals[i]) sh = 2;
      gb_fill_rect(ox + x * cell, oy + y * cell, cell - 1, cell - 1, sh);
    }
  }
  gb_fill_rect(ox + s->px * cell + 1, oy + s->py * cell + 1, cell - 3, cell - 3, 0);
  if (s->won) gb_print(4, 17, "CLEAR");
}

static unsigned char prev;

int main(void) {
  GameCore g;
  unsigned char joy, edge;
  gb_init();
  gc_load(&g, 0);
  prev = 0;
  for (;;) {
    gb_wait_vblank();
    joy = gb_joypad();
    edge = (unsigned char)(joy & (unsigned char)~prev);
    prev = joy;
    if (edge & GB_KEY_UP) gc_try_move(&g, 0, -1);
    if (edge & GB_KEY_DOWN) gc_try_move(&g, 0, 1);
    if (edge & GB_KEY_LEFT) gc_try_move(&g, -1, 0);
    if (edge & GB_KEY_RIGHT) gc_try_move(&g, 1, 0);
    if (edge & GB_KEY_B) gc_undo(&g);
    if (edge & GB_KEY_SELECT) gc_load(&g, g.level);
    if (edge & GB_KEY_START) gc_load(&g, g.level + 1);
    if (edge & GB_KEY_A && g.won) gc_load(&g, g.level + 1);
    draw(&g);
  }
  return 0;
}
