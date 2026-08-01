#include "gbc_hw.h"
#include <stdio.h>

void gbc_init(void) { printf("[gbc] init color 160x144\n"); }
void gbc_wait_vblank(void) {}
unsigned char gbc_joypad(void) { return 0; }
void gbc_cls(GbcColorId id) { (void)id; }
void gbc_fill_rect(int x, int y, int w, int h, GbcColorId id) {
  (void)x; (void)y; (void)w; (void)h; (void)id;
}
void gbc_print(int x, int y, const char *s) {
  (void)x; (void)y;
  if (s) printf("[gbc] %s\n", s);
}
void gbc_set_palette(const unsigned short rgb555[GBC_COL_COUNT]) {
  (void)rgb555;
  printf("[gbc] palette loaded\n");
}
