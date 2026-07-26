#ifndef GFX_H
#define GFX_H

#include <stdint.h>

#define SCREEN_W 480
#define SCREEN_H 272
#define BUF_W    512
#define BUF_H    272

/* ABGR 8888 */
#define COL_BLACK   0xFF000000u
#define COL_WHITE   0xFFFFFFFFu
#define COL_GRAY    0xFF808080u
#define COL_DKGRAY  0xFF303038u
#define COL_CYAN    0xFFFFFF00u
#define COL_BLUE    0xFFFF8030u
#define COL_YELLOW  0xFF00FFFFu
#define COL_ORANGE  0xFF0080FFu
#define COL_RED     0xFF3030FFu
#define COL_PINK    0xFFB060FFu
#define COL_GREEN   0xFF40FF40u
#define COL_LIME    0xFF40FFA0u
#define COL_PURPLE  0xFFFF40A0u
#define COL_SKY     0xFFFFC060u

void gfx_init(void);
void gfx_shutdown(void);
void gfx_begin(uint32_t clear_color);
void gfx_end(void);

void gfx_rect(float x, float y, float w, float h, uint32_t color);
void gfx_rect_border(float x, float y, float w, float h, float t, uint32_t color);

#endif
