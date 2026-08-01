/**
 * DOS 推箱子教学（DJGPP / Open Watcom / Turbo C 思路）。
 * 默认：文本模式 ASCII；定义 USE_MODE13 时尝试 320x200 写显存（DJGPP far 指针示意）。
 */
#include "game_core.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef __DJGPP__
#include <pc.h>
#include <dpmi.h>
#include <go32.h>
#include <sys/farptr.h>
#endif

static void draw_ascii(const GameCore *s) {
  int y, x;
  /* DOS 清屏近似 */
  printf("\nLV%d M%d%s\n", s->level + 1, s->moves, s->won ? " WIN" : "");
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

#ifdef USE_MODE13
static void set_mode13(void) {
#ifdef __DJGPP__
  __dpmi_regs r;
  r.x.ax = 0x13;
  __dpmi_int(0x10, &r);
#else
  /* 其它编译器自行内联 int 10h */
#endif
}

static void plot(int x, int y, unsigned char c) {
#ifdef __DJGPP__
  if (x < 0 || y < 0 || x >= 320 || y >= 200) return;
  _farpokeb(_dos_ds, 0xA0000 + y * 320 + x, c);
#else
  (void)x; (void)y; (void)c;
#endif
}

static void draw_mode13(const GameCore *s) {
  int cell = 200 / (s->h > 0 ? s->h : 1);
  int ox, oy, x, y, a, b;
  if (320 / (s->w > 0 ? s->w : 1) < cell) cell = 320 / (s->w > 0 ? s->w : 1);
  if (cell < 2) cell = 2;
  ox = (320 - cell * s->w) / 2;
  oy = (200 - cell * s->h) / 2;
  for (y = 0; y < 200; y++)
    for (x = 0; x < 320; x++) plot(x, y, 0);
  for (y = 0; y < s->h; y++) {
    for (x = 0; x < s->w; x++) {
      int i = gc_idx(s, x, y);
      unsigned char col = s->walls[i] ? 8 : 1;
      if (s->boxes[i]) col = s->goals[i] ? 10 : 14;
      for (b = 0; b < cell - 1; b++)
        for (a = 0; a < cell - 1; a++)
          plot(ox + x * cell + a, oy + y * cell + b, col);
    }
  }
  for (b = 0; b < cell / 2; b++)
    for (a = 0; a < cell / 2; a++)
      plot(ox + s->px * cell + cell / 4 + a, oy + s->py * cell + cell / 4 + b, 11);
}
#endif

/* 非阻塞读键：DJGPP bioskey；通用 getchar 阻塞 */
static int read_cmd(void) {
#ifdef __DJGPP__
  if (!kbhit()) return 0;
  return getkey() & 0xFF;
#else
  return getchar();
#endif
}

int main(void) {
  GameCore g;
  int c;
  gc_load(&g, 0);
#ifdef USE_MODE13
  set_mode13();
  draw_mode13(&g);
#else
  printf("DOS sokoban — wasd z r n q\n");
  draw_ascii(&g);
#endif
  for (;;) {
    c = read_cmd();
    if (!c) continue;
    if (c == 'q' || c == 'Q' || c == 27) break;
    else if (c == 'w' || c == 'W') gc_try_move(&g, 0, -1);
    else if (c == 's' || c == 'S') gc_try_move(&g, 0, 1);
    else if (c == 'a' || c == 'A') gc_try_move(&g, -1, 0);
    else if (c == 'd' || c == 'D') gc_try_move(&g, 1, 0);
    else if (c == 'z' || c == 'Z') gc_undo(&g);
    else if (c == 'r' || c == 'R') gc_load(&g, g.level);
    else if (c == 'n' || c == 'N') gc_load(&g, g.level + 1);
#ifdef USE_MODE13
    draw_mode13(&g);
#else
    draw_ascii(&g);
#endif
  }
  return 0;
}
