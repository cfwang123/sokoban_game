#ifndef SOKO_GFX_H
#define SOKO_GFX_H
#include "gba.h"

#define CELL 16
#define HUD_H 16
#define VIEW_H (SCREEN_H - HUD_H)

enum {
	TIL_VOID = 0,
	TIL_FLOOR,
	TIL_WALL,
	TIL_GOAL,
	TIL_BOX,
	TIL_BOXG,
	TIL_PLAYER,
	TIL_HUD,
	TIL_PANEL
};

extern const int GFX_TILE;
extern const int GFX_TILE_COUNT;
extern const u16 * const gfx_tiles[];

void gfx_init(void);
u16 *gfx_back(void);
void gfx_clear(u16 c);
void gfx_fill(int x, int y, int w, int h, u16 c);
void gfx_blit_tile(int dx, int dy, int tid);
void gfx_blit_tile_key(int dx, int dy, int tid, u16 key);
void gfx_flip(void);
void gfx_text(int x, int y, const char *s, u16 color);
void gfx_text_shadow(int x, int y, const char *s, u16 color, u16 shadow);

#endif
