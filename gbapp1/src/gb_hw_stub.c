#include "gb_hw.h"
#include <stdio.h>

void gb_init(void) { printf("[gb] init 160x144\n"); }
void gb_wait_vblank(void) {}
unsigned char gb_joypad(void) { return 0; }
void gb_cls(unsigned char shade) { (void)shade; }
void gb_fill_rect(int x, int y, int w, int h, unsigned char shade) {
  (void)x; (void)y; (void)w; (void)h; (void)shade;
}
void gb_print(int x, int y, const char *s) {
  (void)x; (void)y;
  if (s) printf("[gb] %s\n", s);
}
