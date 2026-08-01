/**
 * Linux 帧缓冲推箱子（教学）。
 * 优先：/dev/fb0 填色块；失败则退回终端 ASCII。
 * 键盘：/dev/tty 原始模式读 wasd。
 */
#include "game_core.h"

#include <fcntl.h>
#include <linux/fb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <termios.h>
#include <unistd.h>

static int fb_fd = -1;
static char *fb_mem;
static struct fb_var_screeninfo vinfo;
static struct fb_fix_screeninfo finfo;
static struct termios oldt;

static void tty_raw(void) {
  struct termios t;
  tcgetattr(STDIN_FILENO, &oldt);
  t = oldt;
  t.c_lflag &= ~(ICANON | ECHO);
  tcsetattr(STDIN_FILENO, TCSANOW, &t);
}

static void tty_restore(void) {
  tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
}

static int fb_open(void) {
  fb_fd = open("/dev/fb0", O_RDWR);
  if (fb_fd < 0) return -1;
  if (ioctl(fb_fd, FBIOGET_FSCREENINFO, &finfo) < 0) return -1;
  if (ioctl(fb_fd, FBIOGET_VSCREENINFO, &vinfo) < 0) return -1;
  size_t sz = finfo.smem_len;
  fb_mem = mmap(0, sz, PROT_READ | PROT_WRITE, MAP_SHARED, fb_fd, 0);
  if (fb_mem == MAP_FAILED) {
    fb_mem = NULL;
    return -1;
  }
  return 0;
}

static void put_px(int x, int y, unsigned color) {
  if (!fb_mem || x < 0 || y < 0 || x >= (int)vinfo.xres || y >= (int)vinfo.yres) return;
  long loc = (x + vinfo.xoffset) * (vinfo.bits_per_pixel / 8)
           + (y + vinfo.yoffset) * finfo.line_length;
  if (vinfo.bits_per_pixel == 32) {
    *(unsigned *)(fb_mem + loc) = color;
  } else if (vinfo.bits_per_pixel == 16) {
    *(unsigned short *)(fb_mem + loc) = (unsigned short)color;
  }
}

static void fill_rect(int x, int y, int w, int h, unsigned color) {
  int i, j;
  for (j = 0; j < h; j++)
    for (i = 0; i < w; i++) put_px(x + i, y + j, color);
}

static void draw_fb(const GameCore *s) {
  int cell, ox, oy, x, y;
  if (!fb_mem) return;
  fill_rect(0, 0, (int)vinfo.xres, (int)vinfo.yres, 0x001a1a2e);
  cell = (int)vinfo.xres / (s->w > 0 ? s->w : 1);
  if ((int)vinfo.yres / (s->h > 0 ? s->h : 1) < cell)
    cell = (int)vinfo.yres / (s->h > 0 ? s->h : 1);
  if (cell < 4) cell = 4;
  ox = ((int)vinfo.xres - cell * s->w) / 2;
  oy = ((int)vinfo.yres - cell * s->h) / 2;
  for (y = 0; y < s->h; y++) {
    for (x = 0; x < s->w; x++) {
      int i = gc_idx(s, x, y);
      unsigned col = s->walls[i] ? 0x004a4a6a : 0x003a3a55;
      fill_rect(ox + x * cell, oy + y * cell, cell - 1, cell - 1, col);
      if (s->goals[i]) fill_rect(ox + x * cell + cell / 3, oy + y * cell + cell / 3, cell / 3, cell / 3, 0x00e94560);
      if (s->boxes[i]) fill_rect(ox + x * cell + 2, oy + y * cell + 2, cell - 5, cell - 5,
                                 s->goals[i] ? 0x002ecc71 : 0x00f39c12);
    }
  }
  fill_rect(ox + s->px * cell + cell / 4, oy + s->py * cell + cell / 4, cell / 2, cell / 2, 0x003498db);
}

static void draw_ascii(const GameCore *s) {
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
  fflush(stdout);
}

int main(void) {
  GameCore g;
  int use_fb = (fb_open() == 0);
  tty_raw();
  atexit(tty_restore);
  gc_load(&g, 0);
  if (use_fb) draw_fb(&g); else draw_ascii(&g);
  printf("linuxfb sokoban — wasd z r q  (fb=%s)\n", use_fb ? "yes" : "ascii");
  for (;;) {
    char c;
    if (read(STDIN_FILENO, &c, 1) != 1) break;
    if (c == 'q' || c == 'Q') break;
    else if (c == 'w' || c == 'W') gc_try_move(&g, 0, -1);
    else if (c == 's' || c == 'S') gc_try_move(&g, 0, 1);
    else if (c == 'a' || c == 'A') gc_try_move(&g, -1, 0);
    else if (c == 'd' || c == 'D') gc_try_move(&g, 1, 0);
    else if (c == 'z' || c == 'Z') gc_undo(&g);
    else if (c == 'r' || c == 'R') gc_load(&g, g.level);
    else if (c == 'n' || c == 'N') gc_load(&g, g.level + 1);
    if (use_fb) draw_fb(&g); else draw_ascii(&g);
  }
  if (fb_mem) munmap(fb_mem, finfo.smem_len);
  if (fb_fd >= 0) close(fb_fd);
  return 0;
}
