#ifndef GAME_H
#define GAME_H

#include "nes.h"

/* Zeropage / shared state (defined in main.c) */
extern unsigned char nmi_ready;
extern unsigned char frame_cnt;
extern unsigned char game_state;
extern unsigned char pad1, pad1_prev, pad1_edge;
extern unsigned char sfx_timer;
extern unsigned char level_id;
extern unsigned char map_w, map_h;
extern unsigned char player_x, player_y;
extern unsigned char moves_lo, moves_hi;
extern unsigned char box_count, goal_ok;
extern unsigned char oam[256];

#pragma zpsym ("nmi_ready")
#pragma zpsym ("frame_cnt")
#pragma zpsym ("game_state")
#pragma zpsym ("pad1")
#pragma zpsym ("pad1_prev")
#pragma zpsym ("pad1_edge")
#pragma zpsym ("sfx_timer")
#pragma zpsym ("level_id")
#pragma zpsym ("map_w")
#pragma zpsym ("map_h")
#pragma zpsym ("player_x")
#pragma zpsym ("player_y")
#pragma zpsym ("moves_lo")
#pragma zpsym ("moves_hi")
#pragma zpsym ("box_count")
#pragma zpsym ("goal_ok")

/* levels.c */
extern const unsigned char LEVEL_COUNT;
extern const unsigned char * const level_ptrs[];
extern const unsigned char level_w[];
extern const unsigned char level_h[];
extern const unsigned char sol_len_lo[];
extern const unsigned char sol_len_hi[];
extern const unsigned char * const sol_ptrs[];

/* Music */
void music_init(void);
void music_update(void);
void sfx_move(void);
void sfx_push(void);
void sfx_block(void);
void sfx_undo(void);
void sfx_win(void);
void sfx_reset(void);

#endif
