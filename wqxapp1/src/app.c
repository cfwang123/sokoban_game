#include "app.h"
#include "game.h"
#include "levels_data.h"
#include "pathfinding.h"
#include "ui.h"
#include "wqx/wqx_api.h"

#include <string.h>

static GameState s_game;
static char s_status[40];
static int s_answer;
static int s_anim_dirs[256];
static int s_anim_len;
static int s_anim_pos;

static void set_status(const char *t) {
    strncpy(s_status, t ? t : "", sizeof(s_status) - 1);
    s_status[sizeof(s_status) - 1] = 0;
}

static void refresh_status(void) {
    const char *sol;
    if (s_answer) {
        return;
    }
    if (s_game.won) {
        set_status("CLEAR - OK next");
        return;
    }
    sol = g_wqx_levels[s_game.level_index].solution;
    if (sol && sol[0]) {
        set_status("A:answer  M:menu");
    } else {
        set_status("no answer  M:menu");
    }
}

static void load_level(int idx) {
    if (idx < 0) {
        idx = 0;
    }
    if (idx >= WQX_LEVEL_COUNT) {
        idx = WQX_LEVEL_COUNT - 1;
    }
    s_answer = 0;
    s_anim_len = 0;
    s_anim_pos = 0;
    game_load_level(&s_game, idx);
    wqx_nv_save_u8(WQX_NV_LAST_LEVEL, (unsigned char)idx);
    refresh_status();
}

static void stop_answer(void) {
    s_answer = 0;
    s_anim_len = 0;
    s_anim_pos = 0;
    refresh_status();
}

static void start_answer(void) {
    const char *sol = g_wqx_levels[s_game.level_index].solution;
    int i;
    if (s_game.won || !sol || !sol[0]) {
        set_status("no answer");
        return;
    }
    s_anim_len = 0;
    for (i = 0; sol[i] && s_anim_len < 256; i++) {
        int d = -1;
        char c = sol[i];
        if (c == 'U' || c == 'u') {
            d = 0;
        } else if (c == 'D' || c == 'd') {
            d = 1;
        } else if (c == 'L' || c == 'l') {
            d = 2;
        } else if (c == 'R' || c == 'r') {
            d = 3;
        }
        if (d >= 0) {
            s_anim_dirs[s_anim_len++] = d;
        }
    }
    if (s_anim_len == 0) {
        set_status("no answer");
        return;
    }
    load_level(s_game.level_index);
    s_answer = 1;
    s_anim_pos = 0;
    set_status("playback... A:stop");
}

/** 无触屏：自动寻路到较远空地（演示 BFS）。 */
static void demo_pathfind(void) {
    int x, y, best_x, best_y, best_d, len;
    int path[GAME_MAX_CELLS];

    if (s_game.won || s_answer) {
        return;
    }
    best_x = s_game.player_x;
    best_y = s_game.player_y;
    best_d = -1;
    for (y = 0; y < s_game.height; y++) {
        for (x = 0; x < s_game.width; x++) {
            int i = game_idx(&s_game, x, y);
            int d;
            if (s_game.walls[i] || s_game.boxes[i]) {
                continue;
            }
            d = (x > s_game.player_x ? x - s_game.player_x : s_game.player_x - x) +
                (y > s_game.player_y ? y - s_game.player_y : s_game.player_y - y);
            if (d > best_d) {
                best_d = d;
                best_x = x;
                best_y = y;
            }
        }
    }
    len = path_find(&s_game, best_x, best_y, path, GAME_MAX_CELLS);
    if (len > 0) {
        for (x = 0; x < len; x++) {
            game_try_move_dir(&s_game, path[x]);
            if (s_game.won) {
                break;
            }
        }
    }
    refresh_status();
}

static void handle_key(unsigned edge) {
    if (!edge) {
        return;
    }
    if (s_answer) {
        if (edge & WQX_KEY_ANSWER) {
            stop_answer();
        }
        return;
    }
    if (s_game.won) {
        if (edge & (WQX_KEY_OK | WQX_KEY_NEXT)) {
            load_level(s_game.level_index + 1);
        }
        return;
    }
    if (edge & WQX_KEY_UP) {
        game_try_move_dir(&s_game, 0);
    }
    if (edge & WQX_KEY_DOWN) {
        game_try_move_dir(&s_game, 1);
    }
    if (edge & WQX_KEY_LEFT) {
        game_try_move_dir(&s_game, 2);
    }
    if (edge & WQX_KEY_RIGHT) {
        game_try_move_dir(&s_game, 3);
    }
    if (edge & WQX_KEY_UNDO) {
        game_undo(&s_game);
    }
    if (edge & WQX_KEY_RESET) {
        load_level(s_game.level_index);
        return;
    }
    if (edge & WQX_KEY_PREV) {
        load_level(s_game.level_index - 1);
        return;
    }
    if (edge & WQX_KEY_NEXT) {
        load_level(s_game.level_index + 1);
        return;
    }
    if (edge & WQX_KEY_ANSWER) {
        start_answer();
        return;
    }
    if (edge & WQX_KEY_MENU) {
        demo_pathfind(); /* 教学：菜单键触发 BFS 演示 */
        return;
    }
    if (edge & WQX_KEY_ESC) {
        /* 返回桌面：由 main 循环检测退出；此处仅标记 status */
        set_status("hold ESC to quit");
    }
    refresh_status();
}

int app_run(void) {
    unsigned char last = 0;
    int esc_hold = 0;

    if (wqx_init() != 0) {
        return 1;
    }
    if (wqx_nv_load_u8(WQX_NV_LAST_LEVEL, &last) != 0) {
        last = 0;
    }
    load_level((int)last);

    for (;;) {
        unsigned edge = wqx_key_pressed();

        if (s_answer && s_anim_pos < s_anim_len) {
            game_try_move_dir(&s_game, s_anim_dirs[s_anim_pos++]);
            if (s_game.won || s_anim_pos >= s_anim_len) {
                stop_answer();
            }
            wqx_delay_ms(60);
        } else {
            handle_key(edge);
            if (edge & WQX_KEY_ESC) {
                esc_hold++;
                if (esc_hold > 15) { /* 约长按退出 */
                    break;
                }
            } else {
                esc_hold = 0;
            }
            wqx_delay_ms(33); /* ~30fps 轮询 */
        }

        if (s_game.won) {
            ui_draw_win(&s_game);
        } else {
            ui_draw(&s_game, s_status);
        }
    }

    wqx_shutdown();
    return 0;
}
