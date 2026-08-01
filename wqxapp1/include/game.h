#ifndef WQX_GAME_H
#define WQX_GAME_H

/**
 * 推箱子核心状态（与 html_app / androidapp1 / n81app1 规则对齐）。
 * 纯 C，不依赖文曲星 API，便于 PC 上逻辑复用与单测。
 */

#define GAME_MAX_W 24
#define GAME_MAX_H 20
#define GAME_MAX_CELLS (GAME_MAX_W * GAME_MAX_H)

typedef struct {
    int width;
    int height;
    int level_index;
    int player_x;
    int player_y;
    int moves;
    int won;
    unsigned char walls[GAME_MAX_CELLS];
    unsigned char goals[GAME_MAX_CELLS];
    unsigned char boxes[GAME_MAX_CELLS];
} GameState;

int game_idx(const GameState *s, int x, int y);
int game_load_level(GameState *s, int level_index);
int game_try_move(GameState *s, int dx, int dy);
int game_try_move_dir(GameState *s, int dir); /* 0U 1D 2L 3R */
int game_undo(GameState *s);

#endif
