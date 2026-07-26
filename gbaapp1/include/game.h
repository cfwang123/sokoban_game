#ifndef SOKO_GAME_H
#define SOKO_GAME_H
#include "gba.h"

#define MAP_MAX_W 20
#define MAP_MAX_H 18
#define MAP_MAX (MAP_MAX_W * MAP_MAX_H)
#define HIST_MAX 64

#define C_WALL 0x01
#define C_GOAL 0x02
#define C_BOX 0x04

#define ST_TITLE 0
#define ST_PLAY 1
#define ST_MENU 2
#define ST_ANSWER 3
#define ST_WIN 4

#define MENU_RESET 0
#define MENU_NEXT 1
#define MENU_ANS 2
#define MENU_COUNT 3

typedef struct {
	u8 state;
	u8 level_id;
	u8 map_w, map_h;
	u8 px, py;
	u8 cam_x, cam_y;
	u16 moves;
	u8 box_count, goal_ok;
	u8 menu_sel;
	u8 menu_note; /* 1 = NO ANSWER */
	u8 need_redraw;
	u8 cells[MAP_MAX];
	u8 hist_px[HIST_MAX];
	u8 hist_py[HIST_MAX];
	u8 hist_flag[HIST_MAX];
	u8 hist_bx[HIST_MAX];
	u8 hist_by[HIST_MAX];
	u8 hist_len;
	u16 sol_pos;
	u8 sol_timer;
	u8 hold_t;
	u16 hold_key;
} Game;

extern Game g;

void game_init(void);
void game_update(u16 keys, u16 pressed);
void game_draw(void);

#endif
