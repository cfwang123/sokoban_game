/*
 * Sokoban game logic + polished GU rect rendering
 * Ported from html_app / gbaapp1; PSP shell follows starstrike.
 */
#include "game.h"
#include "gfx.h"
#include "font.h"
#include "levels.h"

#include <pspctrl.h>
#include <stdio.h>
#include <string.h>

#define MAP_MAX_W 20
#define MAP_MAX_H 18
#define MAP_MAX   (MAP_MAX_W * MAP_MAX_H)
#define HIST_MAX  64

#define C_WALL 0x01
#define C_GOAL 0x02
#define C_BOX  0x04

#define ST_TITLE  0
#define ST_PLAY   1
#define ST_MENU   2
#define ST_ANSWER 3
#define ST_WIN    4

#define MENU_RESET 0
#define MENU_NEXT  1
#define MENU_ANS   2
#define MENU_COUNT 3

#define CELL   24.0f
#define HUD_H  28.0f

/* ABGR */
#define COL_BG      0xFF1A1020u
#define COL_FLOOR   0xFF3A2818u
#define COL_FLOOR2  0xFF2E2014u
#define COL_WALL    0xFF707078u
#define COL_WALL_H  0xFFA0A0A8u
#define COL_WALL_S  0xFF404048u
#define COL_GOAL    0xFF3030C0u
#define COL_GOAL_H  0xFF6060F0u
#define COL_BOX     0xFF2080D0u
#define COL_BOX_H   0xFF40A0F0u
#define COL_BOX_S   0xFF104080u
#define COL_BOXG    0xFF30C050u
#define COL_BOXG_H  0xFF50E070u
#define COL_PLAYER  0xFFE0A040u
#define COL_PLAYER2 0xFFFFC060u
#define COL_HUD     0xFF201828u
#define COL_TEXT    0xFFFFFFF0u
#define COL_DIM     0xFFA0A0B0u
#define COL_GOLD    0xFF40E0FFu
#define COL_ERR     0xFF4040FFu
#define COL_PANEL   0xEE181428u
#define COL_BORDER  0xFF806040u

static int running = 1;
static int state = ST_TITLE;
static SceCtrlData pad;
static unsigned int prev_buttons;

static unsigned char map_w, map_h;
static unsigned char level_id;
static unsigned char cells[MAP_MAX];
static unsigned char px, py;
static int cam_x, cam_y;
static unsigned int moves;
static unsigned char box_count, goal_ok;
static unsigned char menu_sel, menu_note;

static unsigned char hist_px[HIST_MAX], hist_py[HIST_MAX], hist_flag[HIST_MAX];
static unsigned char hist_bx[HIST_MAX], hist_by[HIST_MAX];
static unsigned char hist_len;

static unsigned short sol_pos;
static unsigned char sol_timer;
static unsigned char hold_t;
static unsigned int hold_mask;

static int pressed(unsigned int mask)
{
    return (pad.Buttons & mask) && !(prev_buttons & mask);
}

static unsigned short map_index(unsigned char x, unsigned char y)
{
    return (unsigned short)y * map_w + x;
}

static unsigned char cell_at(unsigned char x, unsigned char y)
{
    if (x >= map_w || y >= map_h)
        return C_WALL;
    return cells[map_index(x, y)];
}

static void set_cell(unsigned char x, unsigned char y, unsigned char v)
{
    cells[map_index(x, y)] = v;
}

static void update_cam(void)
{
    int view_w = (int)(SCREEN_W / CELL);
    int view_h = (int)((SCREEN_H - HUD_H) / CELL);
    int cx = (int)px - view_w / 2;
    int cy = (int)py - view_h / 2;
    int max_x = (int)map_w - view_w;
    int max_y = (int)map_h - view_h;
    if (max_x < 0) max_x = 0;
    if (max_y < 0) max_y = 0;
    if (cx < 0) cx = 0;
    if (cy < 0) cy = 0;
    if (cx > max_x) cx = max_x;
    if (cy > max_y) cy = max_y;
    cam_x = (map_w * (int)CELL < SCREEN_W) ? 0 : cx;
    cam_y = (map_h * (int)CELL < (int)(SCREEN_H - HUD_H)) ? 0 : cy;
}

static void check_win(void)
{
    unsigned short i, n = (unsigned short)map_w * map_h;
    unsigned char boxes = 0, on = 0, c;
    for (i = 0; i < n; i++) {
        c = cells[i];
        if (c & C_BOX) {
            boxes++;
            if (c & C_GOAL)
                on++;
        }
    }
    box_count = boxes;
    goal_ok = on;
    if (boxes > 0 && boxes == on) {
        if (state == ST_PLAY || state == ST_ANSWER)
            state = ST_WIN;
    }
}

static void load_level(unsigned char id)
{
    const unsigned char *src;
    unsigned short i, n;
    unsigned char b = 0, ch, x, y;
    unsigned char ppx = 0, ppy = 0;

    if (id >= LEVEL_COUNT)
        id = 0;
    level_id = id;
    map_w = level_w[id];
    map_h = level_h[id];
    src = level_ptrs[id];
    n = (unsigned short)map_w * map_h;
    box_count = 0;

    for (i = 0; i < n; i++) {
        if ((i & 1) == 0)
            b = src[i >> 1];
        ch = (i & 1) ? (unsigned char)(b & 0x0F) : (unsigned char)(b >> 4);
        x = (unsigned char)(i % map_w);
        y = (unsigned char)(i / map_w);
        switch (ch) {
        case 1: cells[i] = C_WALL; break;
        case 2: cells[i] = C_GOAL; break;
        case 3: cells[i] = C_BOX; box_count++; break;
        case 4: cells[i] = (unsigned char)(C_BOX | C_GOAL); box_count++; break;
        case 5: cells[i] = 0; ppx = x; ppy = y; break;
        case 6: cells[i] = C_GOAL; ppx = x; ppy = y; break;
        default: cells[i] = 0; break;
        }
    }
    px = ppx;
    py = ppy;
    moves = 0;
    hist_len = 0;
    sol_pos = 0;
    sol_timer = 0;
    goal_ok = 0;
    check_win();
    if (state == ST_WIN)
        state = ST_PLAY;
    update_cam();
}

static void try_move(int dx, int dy)
{
    unsigned char nx = (unsigned char)(px + dx);
    unsigned char ny = (unsigned char)(py + dy);
    unsigned char c = cell_at(nx, ny);
    unsigned char bx, by, c2;

    if (c & C_WALL)
        return;

    if (c & C_BOX) {
        bx = (unsigned char)(nx + dx);
        by = (unsigned char)(ny + dy);
        c2 = cell_at(bx, by);
        if ((c2 & C_WALL) || (c2 & C_BOX))
            return;
        if (hist_len < HIST_MAX) {
            hist_px[hist_len] = px;
            hist_py[hist_len] = py;
            hist_flag[hist_len] = 1;
            hist_bx[hist_len] = bx;
            hist_by[hist_len] = by;
            hist_len++;
        }
        set_cell(nx, ny, (unsigned char)(c & (unsigned char)~C_BOX));
        set_cell(bx, by, (unsigned char)(c2 | C_BOX));
        px = nx;
        py = ny;
        moves++;
        update_cam();
        check_win();
        return;
    }

    if (hist_len < HIST_MAX) {
        hist_px[hist_len] = px;
        hist_py[hist_len] = py;
        hist_flag[hist_len] = 0;
        hist_len++;
    }
    px = nx;
    py = ny;
    update_cam();
}

static void undo_move(void)
{
    unsigned char f, hpx, hpy, bx, by, fromx, fromy, c, c2;

    if (hist_len == 0)
        return;
    while (hist_len > 0) {
        hist_len--;
        f = hist_flag[hist_len];
        hpx = hist_px[hist_len];
        hpy = hist_py[hist_len];
        if (!f) {
            px = hpx;
            py = hpy;
            continue;
        }
        bx = hist_bx[hist_len];
        by = hist_by[hist_len];
        fromx = px;
        fromy = py;
        c = cell_at(bx, by);
        c2 = cell_at(fromx, fromy);
        set_cell(bx, by, (unsigned char)(c & (unsigned char)~C_BOX));
        set_cell(fromx, fromy, (unsigned char)(c2 | C_BOX));
        px = hpx;
        py = hpy;
        if (moves)
            moves--;
        if (state != ST_ANSWER)
            state = ST_PLAY;
        update_cam();
        check_win();
        return;
    }
    update_cam();
}

static void start_answer(void)
{
    if (sol_len[level_id] == 0 || !sol_ptrs[level_id]) {
        menu_note = 1;
        return;
    }
    state = ST_PLAY;
    load_level(level_id);
    sol_pos = 0;
    sol_timer = 20;
    state = ST_ANSWER;
}

/* ---------- drawing helpers (layered rects = “HD” look) ---------- */

static void draw_floor(float x, float y)
{
    gfx_rect(x, y, CELL, CELL, COL_FLOOR);
    gfx_rect(x + 1, y + 1, CELL - 2, CELL - 2, COL_FLOOR2);
    gfx_rect(x + 2, y + 2, CELL - 4, 1, 0x33FFFFFF);
}

static void draw_wall(float x, float y)
{
    float half = CELL * 0.5f;
    gfx_rect(x, y, CELL, CELL, COL_WALL_S);
    /* 2x2 bricks */
    gfx_rect(x + 1, y + 1, half - 2, half - 2, COL_WALL);
    gfx_rect(x + half + 1, y + 1, half - 2, half - 2, COL_WALL);
    gfx_rect(x + 1, y + half + 1, half - 2, half - 2, COL_WALL);
    gfx_rect(x + half + 1, y + half + 1, half - 2, half - 2, COL_WALL);
    gfx_rect(x + 2, y + 2, half - 5, 2, COL_WALL_H);
    gfx_rect(x + half + 2, y + 2, half - 5, 2, COL_WALL_H);
    gfx_rect_border(x, y, CELL, CELL, 1, COL_WALL_S);
}

static void draw_goal(float x, float y)
{
    float m = 5.0f;
    draw_floor(x, y);
    gfx_rect(x + m, y + m, CELL - m * 2, CELL - m * 2, COL_GOAL);
    gfx_rect(x + m + 2, y + m + 2, CELL - m * 2 - 4, CELL - m * 2 - 4, COL_GOAL_H);
    gfx_rect(x + m + 5, y + m + 5, CELL - m * 2 - 10, CELL - m * 2 - 10, COL_FLOOR2);
}

static void draw_box(float x, float y, int on_goal)
{
    uint32_t base = on_goal ? COL_BOXG : COL_BOX;
    uint32_t hi = on_goal ? COL_BOXG_H : COL_BOX_H;
    uint32_t sh = COL_BOX_S;
    float m = 2.0f;
    gfx_rect(x + m, y + m, CELL - m * 2, CELL - m * 2, sh);
    gfx_rect(x + m + 1, y + m + 1, CELL - m * 2 - 2, CELL - m * 2 - 2, base);
    gfx_rect(x + m + 2, y + m + 2, CELL - m * 2 - 6, 3, hi);
    gfx_rect(x + m + 2, y + m + 2, 3, CELL - m * 2 - 6, hi);
    /* X mark */
    {
        float i;
        for (i = 6; i < CELL - 6; i += 1.5f) {
            gfx_rect(x + i, y + i, 2, 2, sh);
            gfx_rect(x + CELL - 2 - i, y + i, 2, 2, sh);
        }
    }
    gfx_rect_border(x + m, y + m, CELL - m * 2, CELL - m * 2, 1.5f, hi);
}

static void draw_player(float x, float y)
{
    float cx = x + CELL * 0.5f;
    float cy = y + CELL * 0.5f;
    /* shadow */
    gfx_rect(cx - 7, y + CELL - 6, 14, 4, 0x66000000);
    /* body */
    gfx_rect(cx - 6, cy - 2, 12, 10, COL_PLAYER);
    gfx_rect(cx - 5, cy - 1, 10, 3, COL_PLAYER2);
    /* head */
    gfx_rect(cx - 5, cy - 9, 10, 9, 0xFFB0D0FFu);
    gfx_rect(cx - 4, cy - 8, 8, 6, 0xFFC8E0FFu);
    /* eyes */
    gfx_rect(cx - 3, cy - 6, 2, 2, COL_BG);
    gfx_rect(cx + 1, cy - 6, 2, 2, COL_BG);
    /* hat */
    gfx_rect(cx - 6, cy - 11, 12, 3, COL_PLAYER2);
}

static void world_offset(float *ox, float *oy)
{
    *ox = 0.0f;
    *oy = HUD_H;
    if (map_w * CELL < SCREEN_W)
        *ox = (SCREEN_W - map_w * CELL) * 0.5f;
    if (map_h * CELL < SCREEN_H - HUD_H)
        *oy = HUD_H + (SCREEN_H - HUD_H - map_h * CELL) * 0.5f;
}

static void draw_board(void)
{
    float ox, oy;
    int x, y;
    unsigned char c;

    world_offset(&ox, &oy);

    for (y = 0; y < map_h; y++) {
        for (x = 0; x < map_w; x++) {
            float sx = ox + (x - cam_x) * CELL;
            float sy = oy + (y - cam_y) * CELL;
            if (sx + CELL < 0 || sy + CELL < HUD_H)
                continue;
            if (sx > SCREEN_W || sy > SCREEN_H)
                continue;
            c = cell_at((unsigned char)x, (unsigned char)y);
            if (c & C_WALL)
                draw_wall(sx, sy);
            else if (c & C_BOX)
                draw_box(sx, sy, (c & C_GOAL) != 0);
            else if (c & C_GOAL)
                draw_goal(sx, sy);
            else
                draw_floor(sx, sy);
        }
    }

    {
        float sx = ox + (px - cam_x) * CELL;
        float sy = oy + (py - cam_y) * CELL;
        draw_player(sx, sy);
    }
}

static void draw_hud(void)
{
    char buf[64];
    gfx_rect(0, 0, SCREEN_W, HUD_H, COL_HUD);
    gfx_rect(0, HUD_H - 2, SCREEN_W, 2, COL_BORDER);

    snprintf(buf, sizeof(buf), "LV %02d", level_id + 1);
    font_draw(12, 8, 2.0f, buf, COL_GOLD);

    snprintf(buf, sizeof(buf), "MOV %d", moves);
    font_draw(100, 8, 2.0f, buf, COL_TEXT);

    snprintf(buf, sizeof(buf), "BOX %d/%d", goal_ok, box_count);
    font_draw(230, 8, 2.0f, buf, COL_BOX_H);

    if (state == ST_ANSWER)
        font_draw(380, 8, 2.0f, "DEMO", COL_GOLD);
    if (state == ST_WIN)
        font_draw(370, 8, 2.0f, "CLEAR!", 0xFF40FF60u);
}

/* ---------- state machine ---------- */

void game_init(void)
{
    running = 1;
    state = ST_TITLE;
    level_id = 0;
    menu_sel = 0;
    menu_note = 0;
    prev_buttons = 0;
    hold_t = 0;
    hold_mask = 0;
    sceCtrlSetSamplingCycle(0);
    sceCtrlSetSamplingMode(PSP_CTRL_MODE_ANALOG);
}

int game_running(void)
{
    return running;
}

void game_update(void)
{
    int dx = 0, dy = 0;
    unsigned int dpad, edge;

    sceCtrlReadBufferPositive(&pad, 1);

    /* analog as d-pad */
    if (pad.Lx < 64)
        pad.Buttons |= PSP_CTRL_LEFT;
    else if (pad.Lx > 192)
        pad.Buttons |= PSP_CTRL_RIGHT;
    if (pad.Ly < 64)
        pad.Buttons |= PSP_CTRL_UP;
    else if (pad.Ly > 192)
        pad.Buttons |= PSP_CTRL_DOWN;

    dpad = pad.Buttons & (PSP_CTRL_UP | PSP_CTRL_DOWN | PSP_CTRL_LEFT | PSP_CTRL_RIGHT);
    edge = 0;
    if (dpad) {
        if ((dpad & ~prev_buttons) & dpad)
            edge = dpad & ~prev_buttons;
        else if ((pad.Buttons & hold_mask) == hold_mask && hold_mask) {
            hold_t++;
            if (hold_t == 14 || (hold_t > 14 && (hold_t % 5) == 0))
                edge = hold_mask;
        } else {
            hold_mask = dpad;
            hold_t = 0;
            edge = dpad & ~prev_buttons;
        }
        if (edge)
            hold_mask = dpad;
    } else {
        hold_t = 0;
        hold_mask = 0;
    }

    if (state == ST_TITLE) {
        if (pressed(PSP_CTRL_LEFT)) {
            if (level_id == 0)
                level_id = (unsigned char)(LEVEL_COUNT - 1);
            else
                level_id--;
        }
        if (pressed(PSP_CTRL_RIGHT)) {
            level_id++;
            if (level_id >= LEVEL_COUNT)
                level_id = 0;
        }
        if (pressed(PSP_CTRL_START) || pressed(PSP_CTRL_CROSS)) {
            load_level(level_id);
            state = ST_PLAY;
        }
        if (pressed(PSP_CTRL_SELECT))
            running = 0;
        prev_buttons = pad.Buttons;
        return;
    }

    if (state == ST_MENU) {
        if (pressed(PSP_CTRL_CIRCLE) || pressed(PSP_CTRL_SELECT)) {
            state = ST_PLAY;
            menu_note = 0;
        }
        if (pressed(PSP_CTRL_UP)) {
            if (menu_sel == 0)
                menu_sel = MENU_COUNT - 1;
            else
                menu_sel--;
            menu_note = 0;
        }
        if (pressed(PSP_CTRL_DOWN)) {
            menu_sel++;
            if (menu_sel >= MENU_COUNT)
                menu_sel = 0;
            menu_note = 0;
        }
        if (pressed(PSP_CTRL_CROSS) || pressed(PSP_CTRL_START)) {
            if (menu_sel == MENU_RESET) {
                load_level(level_id);
                state = ST_PLAY;
            } else if (menu_sel == MENU_NEXT) {
                level_id++;
                if (level_id >= LEVEL_COUNT)
                    level_id = 0;
                load_level(level_id);
                state = ST_PLAY;
            } else {
                /* ANSWER: start_answer sets ST_ANSWER or menu_note=1 */
                start_answer();
            }
        }
        prev_buttons = pad.Buttons;
        return;
    }

    if (state == ST_WIN) {
        if (pressed(PSP_CTRL_CROSS) || pressed(PSP_CTRL_START)) {
            level_id++;
            if (level_id >= LEVEL_COUNT)
                level_id = 0;
            load_level(level_id);
            state = ST_PLAY;
        }
        if (pressed(PSP_CTRL_CIRCLE))
            state = ST_TITLE;
        prev_buttons = pad.Buttons;
        return;
    }

    if (state == ST_ANSWER) {
        if (pressed(PSP_CTRL_CIRCLE) || pressed(PSP_CTRL_START) || pressed(PSP_CTRL_SELECT)) {
            state = ST_PLAY;
            prev_buttons = pad.Buttons;
            return;
        }
        if (sol_timer) {
            sol_timer--;
        } else {
            sol_timer = 4;
            if (sol_pos >= sol_len[level_id]) {
                state = ST_PLAY;
            } else {
                unsigned char step = sol_ptrs[level_id][sol_pos++];
                dx = dy = 0;
                if (step == SOL_U) dy = -1;
                else if (step == SOL_D) dy = 1;
                else if (step == SOL_L) dx = -1;
                else if (step == SOL_R) dx = 1;
                if (dx || dy)
                    try_move(dx, dy);
            }
        }
        prev_buttons = pad.Buttons;
        return;
    }

    /* PLAY */
    if (pressed(PSP_CTRL_START)) {
        menu_sel = 0;
        menu_note = 0;
        state = ST_MENU;
        prev_buttons = pad.Buttons;
        return;
    }
    if (pressed(PSP_CTRL_SELECT)) {
        load_level(level_id);
        prev_buttons = pad.Buttons;
        return;
    }
    if (pressed(PSP_CTRL_CIRCLE) || pressed(PSP_CTRL_SQUARE)) {
        undo_move();
        prev_buttons = pad.Buttons;
        return;
    }

    if (edge & PSP_CTRL_UP) dy = -1;
    else if (edge & PSP_CTRL_DOWN) dy = 1;
    else if (edge & PSP_CTRL_LEFT) dx = -1;
    else if (edge & PSP_CTRL_RIGHT) dx = 1;
    if (dx || dy)
        try_move(dx, dy);

    prev_buttons = pad.Buttons;
}

void game_draw(void)
{
    char buf[48];
    const char *items[3] = {"RESET", "NEXT", "ANSWER"};
    int i;

    if (state == ST_TITLE) {
        gfx_begin(COL_BG);
        /* decorative grid */
        for (i = 0; i < 8; i++) {
            draw_wall(40.0f + i * 28.0f, 40.0f);
            draw_floor(40.0f + i * 28.0f, 70.0f);
        }
        draw_box(120, 100, 0);
        draw_box(160, 100, 1);
        draw_goal(200, 100);
        draw_player(240, 100);

        font_draw_centered(SCREEN_W * 0.5f, 140, 4.0f, "SOKOBAN", COL_GOLD);
        font_draw_centered(SCREEN_W * 0.5f, 175, 2.0f, "PSP REMAKE", COL_DIM);
        font_draw_centered(SCREEN_W * 0.5f, 200, 2.0f, "PRESS START", COL_TEXT);
        snprintf(buf, sizeof(buf), "LEVEL %02d / %d", level_id + 1, LEVEL_COUNT);
        font_draw_centered(SCREEN_W * 0.5f, 225, 2.0f, buf, COL_PLAYER2);
        font_draw_centered(SCREEN_W * 0.5f, 248, 1.5f, "LEFT RIGHT SELECT LEVEL", COL_DIM);
        gfx_end();
        return;
    }

    gfx_begin(COL_BG);
    draw_board();
    draw_hud();

    if (state == ST_WIN) {
        gfx_rect(90, 100, 300, 70, COL_PANEL);
        gfx_rect_border(90, 100, 300, 70, 2, COL_GOLD);
        font_draw_centered(SCREEN_W * 0.5f, 115, 3.0f, "LEVEL CLEAR!", 0xFF40FF60u);
        font_draw_centered(SCREEN_W * 0.5f, 145, 2.0f, "X:NEXT  O:TITLE", COL_DIM);
    }

    if (state == ST_MENU) {
        gfx_rect(120, 70, 240, 150, COL_PANEL);
        gfx_rect_border(120, 70, 240, 150, 2, COL_BORDER);
        font_draw_centered(SCREEN_W * 0.5f, 85, 3.0f, "MENU", COL_GOLD);
        for (i = 0; i < MENU_COUNT; i++) {
            uint32_t col = (i == menu_sel) ? COL_GOLD : COL_DIM;
            if (i == menu_sel)
                font_draw(150, 120 + i * 24, 2.5f, ">", COL_GOLD);
            font_draw(175, 120 + i * 24, 2.5f, items[i], col);
        }
        if (menu_note)
            font_draw_centered(SCREEN_W * 0.5f, 195, 2.0f, "NO ANSWER", COL_ERR);
        else
            font_draw_centered(SCREEN_W * 0.5f, 195, 1.5f, "X:OK  O:BACK", COL_DIM);
    }

    gfx_end();
}
