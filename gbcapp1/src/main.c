/**
 * Game Boy Color 推箱子（教学）。
 * 相对 gbapp1：色块用逻辑色 ID + 调色板，可在 CGB 上显示多彩箱子/目标。
 */
#include "game_core.h"
#include "gbc_hw.h"

#include <stdio.h>

static const unsigned short kPalette[GBC_COL_COUNT] = {
    0x7FFF, /* BG 白 */
    0x3DEF, /* floor */
    0x2108, /* wall */
    0x001F, /* goal 红倾向 */
    0x01FF, /* box 橙 */
    0x03E0, /* box ok 绿 */
    0x7C00, /* player 蓝倾向 */
};

static void draw(const GameCore *s) {
  int cell, ox, oy, x, y;
  char line[24];
  gbc_cls(GBC_COL_BG);
  sprintf(line, "CGB L%d M%d", s->level + 1, s->moves);
  gbc_print(0, 0, line);

  cell = GBC_LCD_W / (s->w > 0 ? s->w : 1);
  if ((GBC_LCD_H - 16) / (s->h > 0 ? s->h : 1) < cell)
    cell = (GBC_LCD_H - 16) / (s->h > 0 ? s->h : 1);
  if (cell < 4) cell = 4;
  ox = (GBC_LCD_W - cell * s->w) / 2;
  oy = 16 + ((GBC_LCD_H - 16) - cell * s->h) / 2;

  for (y = 0; y < s->h; y++) {
    for (x = 0; x < s->w; x++) {
      int i = gc_idx(s, x, y);
      GbcColorId c = GBC_COL_FLOOR;
      if (s->walls[i]) c = GBC_COL_WALL;
      else if (s->boxes[i]) c = s->goals[i] ? GBC_COL_BOX_OK : GBC_COL_BOX;
      else if (s->goals[i]) c = GBC_COL_GOAL;
      gbc_fill_rect(ox + x * cell, oy + y * cell, cell - 1, cell - 1, c);
    }
  }
  gbc_fill_rect(ox + s->px * cell + 1, oy + s->py * cell + 1, cell - 3, cell - 3, GBC_COL_PLAYER);
  if (s->won) gbc_print(3, 17, "CLEAR!");
}

static unsigned char prev;

int main(void) {
  GameCore g;
  unsigned char joy, edge;
  gbc_init();
  gbc_set_palette(kPalette);
  gc_load(&g, 0);
  prev = 0;
  for (;;) {
    gbc_wait_vblank();
    joy = gbc_joypad();
    edge = (unsigned char)(joy & (unsigned char)~prev);
    prev = joy;
    if (edge & GBC_KEY_UP) gc_try_move(&g, 0, -1);
    if (edge & GBC_KEY_DOWN) gc_try_move(&g, 0, 1);
    if (edge & GBC_KEY_LEFT) gc_try_move(&g, -1, 0);
    if (edge & GBC_KEY_RIGHT) gc_try_move(&g, 1, 0);
    if (edge & GBC_KEY_B) gc_undo(&g);
    if (edge & GBC_KEY_SELECT) gc_load(&g, g.level);
    if (edge & GBC_KEY_START) gc_load(&g, g.level + 1);
    if ((edge & GBC_KEY_A) && g.won) gc_load(&g, g.level + 1);
    draw(&g);
  }
  return 0;
}
