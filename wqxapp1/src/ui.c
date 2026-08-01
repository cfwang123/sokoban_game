#include "ui.h"
#include "levels_data.h"
#include "wqx/wqx_api.h"

#include <stdio.h>
#include <string.h>

/* 灰度约定：浅底深物，贴近纸白墨黑词典屏 */
enum {
    G_BG = 0,
    G_PANEL = 3,
    G_FLOOR = 2,
    G_WALL = 10,
    G_GOAL = 12,
    G_BOX = 8,
    G_BOX_OK = 14,
    G_PLAYER = 15,
    G_TEXT = 15,
    G_MUTED = 9
};

void ui_draw(const GameState *s, const char *status) {
    char line[48];
    int board_top = 20;
    int board_bottom = WQX_LCD_H - 14;
    int board_h = board_bottom - board_top;
    int cell, ox, oy, x, y;

    wqx_clear(G_BG);

    /* 顶栏 */
    wqx_fill_rect(0, 0, WQX_LCD_W, 18, G_PANEL);
    if (s) {
        /* 仅 ASCII，避免依赖中文字库 API */
        sprintf(line, "LV%d/%d %s", s->level_index + 1, WQX_LEVEL_COUNT,
                g_wqx_levels[s->level_index].name);
        if ((int)strlen(line) > 28) {
            line[28] = 0;
        }
        wqx_draw_text(2, 2, line, G_TEXT);
        sprintf(line, "M:%d", s->moves);
        wqx_draw_text(WQX_LCD_W - 36, 2, line, G_MUTED);
    }
    if (status && status[0]) {
        wqx_draw_text(2, 10, status, G_MUTED);
    }

    if (!s || s->width <= 0 || s->height <= 0) {
        wqx_flush();
        return;
    }

    cell = board_h / s->height;
    if (WQX_LCD_W / s->width < cell) {
        cell = WQX_LCD_W / s->width;
    }
    if (cell < 4) {
        cell = 4;
    }
    ox = (WQX_LCD_W - cell * s->width) / 2;
    oy = board_top + (board_h - cell * s->height) / 2;

    for (y = 0; y < s->height; y++) {
        for (x = 0; x < s->width; x++) {
            int i = game_idx(s, x, y);
            int px = ox + x * cell;
            int py = oy + y * cell;
            if (s->walls[i]) {
                wqx_fill_rect(px, py, cell, cell, G_WALL);
            } else {
                wqx_fill_rect(px, py, cell, cell, G_FLOOR);
                wqx_draw_rect(px, py, cell, cell, G_MUTED);
            }
            if (s->goals[i] && !s->walls[i]) {
                int r = cell / 5;
                if (r < 1) {
                    r = 1;
                }
                wqx_fill_circle(px + cell / 2, py + cell / 2, r, G_GOAL);
            }
            if (s->boxes[i]) {
                int m = cell / 8;
                if (m < 1) {
                    m = 1;
                }
                wqx_fill_rect(px + m, py + m, cell - 2 * m, cell - 2 * m,
                              s->goals[i] ? G_BOX_OK : G_BOX);
            }
        }
    }

    {
        int px = ox + s->player_x * cell + cell / 2;
        int py = oy + s->player_y * cell + cell / 2;
        int r = (cell * 35) / 100;
        if (r < 2) {
            r = 2;
        }
        wqx_fill_circle(px, py, r, G_PLAYER);
    }

    /* 底栏键位提示（ASCII） */
    wqx_fill_rect(0, WQX_LCD_H - 12, WQX_LCD_W, 12, G_PANEL);
    wqx_draw_text(2, WQX_LCD_H - 10, "U/D/L/R move  Z undo  R reset", G_MUTED);

    wqx_flush();
}

void ui_draw_win(const GameState *s) {
    char line[32];
    int bw = 140;
    int bh = 50;
    int bx = (WQX_LCD_W - bw) / 2;
    int by = (WQX_LCD_H - bh) / 2;

    ui_draw(s, "CLEAR");
    wqx_fill_rect(bx, by, bw, bh, G_PANEL);
    wqx_draw_rect(bx, by, bw, bh, G_TEXT);
    wqx_draw_text(bx + 30, by + 10, "LEVEL CLEAR!", G_TEXT);
    if (s) {
        sprintf(line, "moves: %d", s->moves);
        wqx_draw_text(bx + 40, by + 24, line, G_MUTED);
    }
    wqx_draw_text(bx + 20, by + 36, "OK=next  ESC=menu", G_MUTED);
    wqx_flush();
}
