/**
 * Game Boy 硬件抽象（教学）。
 * 真机/GBDK：用 joypad()、set_bkg_tiles 等替换下列函数。
 * 分辨率：160×144，4 灰阶。
 */
#ifndef GB_HW_H
#define GB_HW_H

#define GB_LCD_W 160
#define GB_LCD_H 144

/* 键位掩码（与 GBDK J_ 系列对应） */
#define GB_KEY_RIGHT 0x01
#define GB_KEY_LEFT 0x02
#define GB_KEY_UP 0x04
#define GB_KEY_DOWN 0x08
#define GB_KEY_A 0x10
#define GB_KEY_B 0x20
#define GB_KEY_SELECT 0x40
#define GB_KEY_START 0x80

void gb_init(void);
void gb_wait_vblank(void);
unsigned char gb_joypad(void); /* 当前按下 */
void gb_cls(unsigned char shade); /* 0 白 .. 3 黑 */
void gb_fill_rect(int x, int y, int w, int h, unsigned char shade);
void gb_print(int x, int y, const char *s); /* 8x8 字模坐标：字符格 */

#endif
