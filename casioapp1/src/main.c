/**
 * Casio 图形计算器类推箱子（教学抽象）。
 *
 * 真实机型差异极大：
 *  - fx-9860G SDK / Graph 75+E 等使用厂商 syscall / Bdisp
 *  - 部分机型仅能 Basic
 * 本文件用「逻辑 128x64 点阵」+ 键码约定演示结构，
 * 真机时替换 put_pixel / get_key 为 SDK 调用。
 */
#include "game_core.h"

#define LCD_W 128
#define LCD_H 64

static unsigned char vram[LCD_W * LCD_H / 8];

void put_pixel(int x, int y, int on) {
  if (x < 0 || y < 0 || x >= LCD_W || y >= LCD_H) return;
  int i = y * LCD_W + x;
  if (on) vram[i / 8] |= (1u << (i % 8));
  else vram[i / 8] &= ~(1u << (i % 8));
}

void lcd_clear(void) { int i; for (i = 0; i < (int)sizeof(vram); i++) vram[i] = 0; }

void lcd_flush(void) {
  /* 真机：Bdisp_PutDisp_DD / memcpy 到显存；教学：无操作 */
}

/* Casio 常见：方向键、EXE、EXIT、F1.. */
enum { KEY_UP = 1, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_EXE, KEY_EXIT, KEY_F1, KEY_F2 };

int get_key(void) {
  /* 真机：GetKey / key matrix；教学桩返回 0 */
  return 0;
}

void draw_game(const GameCore *s) {
  int cell, ox, oy, x, y;
  lcd_clear();
  cell = LCD_W / (s->w > 0 ? s->w : 1);
  if (LCD_H / (s->h > 0 ? s->h : 1) < cell) cell = LCD_H / (s->h > 0 ? s->h : 1);
  if (cell < 2) cell = 2;
  ox = (LCD_W - cell * s->w) / 2;
  oy = (LCD_H - cell * s->h) / 2;
  for (y = 0; y < s->h; y++) {
    for (x = 0; x < s->w; x++) {
      int i = gc_idx(s, x, y);
      int px = ox + x * cell, py = oy + y * cell, a, b;
      if (s->walls[i]) {
        for (b = 0; b < cell; b++)
          for (a = 0; a < cell; a++) put_pixel(px + a, py + b, 1);
      } else if (s->boxes[i]) {
        for (b = 1; b < cell - 1; b++)
          for (a = 1; a < cell - 1; a++) put_pixel(px + a, py + b, 1);
      } else if (s->goals[i]) {
        put_pixel(px + cell / 2, py + cell / 2, 1);
      }
    }
  }
  {
    int px = ox + s->px * cell + cell / 2;
    int py = oy + s->py * cell + cell / 2;
    put_pixel(px, py, 1);
    put_pixel(px - 1, py, 1);
    put_pixel(px + 1, py, 1);
    put_pixel(px, py - 1, 1);
    put_pixel(px, py + 1, 1);
  }
  lcd_flush();
}

/* 主机模拟入口名 main；Casio 工程可能是 AddIn_main */
#ifdef CASIO_ADDIN
int AddIn_main(int isAppli, unsigned short opt) {
  (void)isAppli; (void)opt;
#else
int main(void) {
#endif
  GameCore g;
  gc_load(&g, 0); /* 使用最小关：mini 集中的 1 L 等 */
  draw_game(&g);
  for (;;) {
    int k = get_key();
    if (k == KEY_EXIT) break;
    else if (k == KEY_UP) gc_try_move(&g, 0, -1);
    else if (k == KEY_DOWN) gc_try_move(&g, 0, 1);
    else if (k == KEY_LEFT) gc_try_move(&g, -1, 0);
    else if (k == KEY_RIGHT) gc_try_move(&g, 1, 0);
    else if (k == KEY_F1) gc_undo(&g);
    else if (k == KEY_F2) gc_load(&g, g.level);
    else if (k == KEY_EXE && g.won) gc_load(&g, g.level + 1);
    if (k) draw_game(&g);
  }
  return 0;
}
