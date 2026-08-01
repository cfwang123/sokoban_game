/**
 * Nintendo DS 硬件抽象（教学 / libnds 风格）。
 * 上屏 256×192 画棋盘，下屏 256×192 画 HUD + 触摸虚拟键。
 */
#ifndef NDS_HW_H
#define NDS_HW_H

#define NDS_W 256
#define NDS_H 192

#define NDS_KEY_A 0x0001
#define NDS_KEY_B 0x0002
#define NDS_KEY_SELECT 0x0004
#define NDS_KEY_START 0x0008
#define NDS_KEY_RIGHT 0x0010
#define NDS_KEY_LEFT 0x0020
#define NDS_KEY_UP 0x0040
#define NDS_KEY_DOWN 0x0080
#define NDS_KEY_R 0x0100
#define NDS_KEY_L 0x0200
#define NDS_KEY_X 0x0400
#define NDS_KEY_Y 0x0800
#define NDS_KEY_TOUCH 0x1000

typedef struct {
  int x, y;
  int touched; /* 1=按下 */
} NdsTouch;

void nds_init(void);
void nds_wait_vblank(void);
unsigned nds_keys_down(void); /* 边沿：本帧新按下 */
unsigned nds_keys_held(void);
void nds_touch_read(NdsTouch *out);

/* 上屏 */
void nds_top_cls(unsigned rgb15);
void nds_top_fill(int x, int y, int w, int h, unsigned rgb15);
void nds_top_print(int x, int y, const char *s);

/* 下屏 */
void nds_sub_cls(unsigned rgb15);
void nds_sub_fill(int x, int y, int w, int h, unsigned rgb15);
void nds_sub_print(int x, int y, const char *s);

#endif
