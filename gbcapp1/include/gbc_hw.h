/**
 * Game Boy Color 硬件抽象（教学）。
 * 在 GB 基础上增加调色板（BGP/OBP 与 CGB 调色板 RAM）。
 */
#ifndef GBC_HW_H
#define GBC_HW_H

#define GBC_LCD_W 160
#define GBC_LCD_H 144

#define GBC_KEY_RIGHT 0x01
#define GBC_KEY_LEFT 0x02
#define GBC_KEY_UP 0x04
#define GBC_KEY_DOWN 0x08
#define GBC_KEY_A 0x10
#define GBC_KEY_B 0x20
#define GBC_KEY_SELECT 0x40
#define GBC_KEY_START 0x80

/* 逻辑色：墙/地/目标/箱/箱OK/玩家 */
typedef enum {
  GBC_COL_BG = 0,
  GBC_COL_FLOOR,
  GBC_COL_WALL,
  GBC_COL_GOAL,
  GBC_COL_BOX,
  GBC_COL_BOX_OK,
  GBC_COL_PLAYER,
  GBC_COL_COUNT
} GbcColorId;

void gbc_init(void);
void gbc_wait_vblank(void);
unsigned char gbc_joypad(void);
void gbc_cls(GbcColorId id);
void gbc_fill_rect(int x, int y, int w, int h, GbcColorId id);
void gbc_print(int x, int y, const char *s);
/** 加载 CGB 背景调色板（RGB555 示意，真机写 FF68/FF69） */
void gbc_set_palette(const unsigned short rgb555[GBC_COL_COUNT]);

#endif
