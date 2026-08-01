#include "nds_hw.h"
#include <stdio.h>
#include <string.h>

void nds_init(void) { printf("[nds] dual screen init\n"); }
void nds_wait_vblank(void) {}
unsigned nds_keys_down(void) { return 0; }
unsigned nds_keys_held(void) { return 0; }
void nds_touch_read(NdsTouch *out) {
  if (out) memset(out, 0, sizeof(*out));
}
void nds_top_cls(unsigned rgb15) { (void)rgb15; }
void nds_top_fill(int x, int y, int w, int h, unsigned rgb15) {
  (void)x; (void)y; (void)w; (void)h; (void)rgb15;
}
void nds_top_print(int x, int y, const char *s) {
  (void)x; (void)y;
  if (s) printf("[nds-top] %s\n", s);
}
void nds_sub_cls(unsigned rgb15) { (void)rgb15; }
void nds_sub_fill(int x, int y, int w, int h, unsigned rgb15) {
  (void)x; (void)y; (void)w; (void)h; (void)rgb15;
}
void nds_sub_print(int x, int y, const char *s) {
  (void)x; (void)y;
  if (s) printf("[nds-sub] %s\n", s);
}
