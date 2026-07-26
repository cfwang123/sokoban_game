#ifndef FONT_H
#define FONT_H

#include <stdint.h>

/* 5x7 bitmap font, drawn as filled rects. */
void font_draw_char(float x, float y, float scale, char c, uint32_t color);
void font_draw(float x, float y, float scale, const char *text, uint32_t color);
void font_draw_centered(float cx, float y, float scale, const char *text, uint32_t color);
float font_width(const char *text, float scale);

#endif
