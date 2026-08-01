/**
 * NDS 推箱子（教学）。
 * 上屏：地图；下屏：步数/按钮区；触屏点下屏虚拟方向或上屏格子寻路（简化：仅下屏 D-pad）。
 * 真机：devkitARM + libnds，替换 nds_hw_stub。
 */
#include "game_core.h"
#include "nds_hw.h"

#include <stdio.h>

#define RGB(r, g, b) ((((r) >> 3) & 0x1F) | ((((g) >> 3) & 0x1F) << 5) | ((((b) >> 3) & 0x1F) << 10))

static void draw_top(const GameCore *s) {
  int cell, ox, oy, x, y;
  nds_top_cls(RGB(26, 26, 46));
  cell = NDS_W / (s->w > 0 ? s->w : 1);
  if (NDS_H / (s->h > 0 ? s->h : 1) < cell) cell = NDS_H / (s->h > 0 ? s->h : 1);
  if (cell < 4) cell = 4;
  ox = (NDS_W - cell * s->w) / 2;
  oy = (NDS_H - cell * s->h) / 2;
  for (y = 0; y < s->h; y++) {
    for (x = 0; x < s->w; x++) {
      int i = gc_idx(s, x, y);
      unsigned c = RGB(58, 58, 85);
      if (s->walls[i]) c = RGB(74, 74, 106);
      else if (s->boxes[i]) c = s->goals[i] ? RGB(46, 204, 113) : RGB(243, 156, 18);
      else if (s->goals[i]) c = RGB(233, 69, 96);
      nds_top_fill(ox + x * cell, oy + y * cell, cell - 1, cell - 1, c);
    }
  }
  nds_top_fill(ox + s->px * cell + 2, oy + s->py * cell + 2, cell - 5, cell - 5, RGB(52, 152, 219));
}

static void draw_sub(const GameCore *s) {
  char line[32];
  nds_sub_cls(RGB(22, 33, 62));
  sprintf(line, "LV%d  moves %d%s", s->level + 1, s->moves, s->won ? " WIN" : "");
  nds_sub_print(8, 8, line);
  nds_sub_print(8, 24, "D-pad move  B undo");
  nds_sub_print(8, 40, "X reset  Y next");
  /* 虚拟键热区（下屏） */
  nds_sub_fill(104, 80, 40, 32, RGB(15, 52, 96));  /* up */
  nds_sub_fill(64, 120, 40, 32, RGB(15, 52, 96));   /* left */
  nds_sub_fill(104, 120, 40, 32, RGB(15, 52, 96));  /* down */
  nds_sub_fill(144, 120, 40, 32, RGB(15, 52, 96));  /* right */
  nds_sub_print(116, 90, "^");
  nds_sub_print(76, 130, "<");
  nds_sub_print(116, 130, "v");
  nds_sub_print(156, 130, ">");
}

static int touch_in(const NdsTouch *t, int x, int y, int w, int h) {
  return t->touched && t->x >= x && t->x < x + w && t->y >= y && t->y < y + h;
}

int main(void) {
  GameCore g;
  NdsTouch touch;
  nds_init();
  gc_load(&g, 0);
  for (;;) {
    unsigned down;
    nds_wait_vblank();
    down = nds_keys_down();
    nds_touch_read(&touch);

    if (down & NDS_KEY_UP) gc_try_move(&g, 0, -1);
    if (down & NDS_KEY_DOWN) gc_try_move(&g, 0, 1);
    if (down & NDS_KEY_LEFT) gc_try_move(&g, -1, 0);
    if (down & NDS_KEY_RIGHT) gc_try_move(&g, 1, 0);
    if (down & NDS_KEY_B) gc_undo(&g);
    if (down & NDS_KEY_X) gc_load(&g, g.level);
    if (down & NDS_KEY_Y) gc_load(&g, g.level + 1);
    if ((down & NDS_KEY_A) && g.won) gc_load(&g, g.level + 1);

    /* 下屏触控 D-pad */
    if (touch_in(&touch, 104, 80, 40, 32)) gc_try_move(&g, 0, -1);
    if (touch_in(&touch, 104, 120, 40, 32)) gc_try_move(&g, 0, 1);
    if (touch_in(&touch, 64, 120, 40, 32)) gc_try_move(&g, -1, 0);
    if (touch_in(&touch, 144, 120, 40, 32)) gc_try_move(&g, 1, 0);

    draw_top(&g);
    draw_sub(&g);
  }
  return 0;
}
