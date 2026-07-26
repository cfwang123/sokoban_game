/*
 * FC Sokoban — main game logic in C (cc65)
 * Ported from html_app; NES boot/NMI stay in assembly (see reset.s / nmi.s).
 */
#include "game.h"

/* ---- Zeropage state ---- */
#pragma bss-name (push, "ZEROPAGE")
unsigned char nmi_ready;
unsigned char frame_cnt;
unsigned char game_state;
unsigned char pad1, pad1_prev, pad1_edge;
unsigned char sfx_timer;
unsigned char level_id;
unsigned char map_w, map_h;
unsigned char player_x, player_y;
unsigned char moves_lo, moves_hi;
unsigned char box_count, goal_ok;
unsigned char oam_idx;
unsigned char off_x, off_y;   /* screen centering offset in tiles */
unsigned char hold_dir;       /* last held direction bit */
unsigned char hold_timer;
unsigned char redraw_all;     /* 1 = full nametable redraw (mask off) */
unsigned char hud_dirty;      /* 1 = only refresh HUD row (incremental) */
unsigned char menu_sel;       /* 0=reset 1=next 2=answer */
unsigned char menu_note;      /* 1 = show NO ANSWER on menu */
unsigned char sol_timer;      /* frames until next solution step */
unsigned char sol_pos_lo;     /* solution playback index */
unsigned char sol_pos_hi;
#pragma bss-name (pop)

#pragma bss-name (push, "OAM")
unsigned char oam[256];
#pragma bss-name (pop)

/* map_cells[y * map_w + x]: C_WALL | C_GOAL | C_BOX */
unsigned char map_cells[MAP_MAX];

/* Undo: store previous player pos + optional box move */
/* hist_px/py: player before move; hist_flag bit0=pushed, hist_bx/by = box dest (from = old player target) */
unsigned char hist_px[HIST_MAX];
unsigned char hist_py[HIST_MAX];
unsigned char hist_flag[HIST_MAX];
unsigned char hist_bx[HIST_MAX];
unsigned char hist_by[HIST_MAX];
unsigned char hist_len;

/* dirty tile queue for partial VRAM updates (applied next frame before nmi) */
#define DIRTY_MAX 8
unsigned char dirty_x[DIRTY_MAX];
unsigned char dirty_y[DIRTY_MAX];
unsigned char dirty_n;

/* ---- forward decls ---- */
static void read_pad(void);
static void wait_vblank(void);
static void clear_nametable(void);
static void fill_attr(void);
static void clear_oam(void);
static void put_spr(unsigned char y, unsigned char tile, unsigned char attr, unsigned char x);
static void draw_title(void);
static void draw_title_sprites(void);
static void draw_level_full(void);
static void draw_menu_screen(void);
static void draw_menu_cursor(void);
static void draw_sprites(void);
static void draw_hud_bg(void);
static void fill_level_attr(void);
static void apply_dirty(void);
static void mark_dirty(unsigned char x, unsigned char y);
static void load_level(unsigned char id);
static void reset_level(void);
static void try_move(signed char dx, signed char dy);
static void undo_move(void);
static void check_win(void);
static unsigned char cell_at(unsigned char x, unsigned char y);
static void set_cell(unsigned char x, unsigned char y, unsigned char v);
static unsigned char tile_for_cell(unsigned char c);
static void update_title(void);
static void update_play(void);
static void update_win(void);
static void update_menu(void);
static void update_answer(void);
static void open_menu(void);
static void start_answer(void);
static void stop_answer(void);
static unsigned sol_length(unsigned char id);
static void poke_bg_tile(unsigned char tx, unsigned char ty, unsigned char tile);
static unsigned char char_to_spr(char c);
static unsigned char char_to_bg(char c);
static void put_text(unsigned char y, unsigned char x, const char *s, unsigned char attr);
static void put_bg_char(unsigned char tx, unsigned char ty, char ch);
static void put_bg_str(unsigned char tx, unsigned char ty, const char *s);
static void put_bg_num2(unsigned char tx, unsigned char ty, unsigned char n);
static void put_bg_num3(unsigned char tx, unsigned char ty, unsigned lo, unsigned char hi);

/* ================================================================ */
void main(void)
{
    game_state = ST_TITLE;
    level_id = 0;
    music_init();
    draw_title();

    /* bit7 NMI | bit4=0 BG@$0000 | bit3=1 SPR@$1000 → 0x88
     * (0x90 was wrong: it swaps BG/SPR pattern tables) */
    PPUCTRL = 0x88;
    nmi_ready = 1;

    for (;;) {
        while (nmi_ready)
            ;

        /*
         * VRAM updates immediately after NMI (still in / near vblank).
         * Full redraw: mask off. Incremental dirty: never blank the screen.
         */
        if (redraw_all) {
            PPUMASK = 0;
            wait_vblank();
            if (game_state == ST_TITLE)
                draw_title();
            else if (game_state == ST_MENU)
                draw_menu_screen();
            else
                draw_level_full();
            redraw_all = 0;
            dirty_n = 0;
            hud_dirty = 0;
            PPUSCROLL = 0;
            PPUSCROLL = 0;
        } else if (dirty_n || hud_dirty) {
            /* incremental only — keep PPUMASK on, no full clear */
            apply_dirty();
            if (hud_dirty) {
                draw_hud_bg();
                hud_dirty = 0;
            }
            PPUSCROLL = 0;
            PPUSCROLL = 0;
        }

        read_pad();

        switch (game_state) {
        case ST_TITLE:  update_title();  break;
        case ST_PLAY:   update_play();   break;
        case ST_MENU:   update_menu();   break;
        case ST_ANSWER: update_answer(); break;
        default:        update_win();    break;
        }

        clear_oam();
        if (game_state == ST_TITLE) {
            draw_title_sprites();
        } else if (game_state == ST_MENU) {
            draw_menu_cursor();
        } else if (game_state == ST_PLAY || game_state == ST_WIN ||
                   game_state == ST_ANSWER) {
            draw_sprites();
            if (game_state == ST_WIN)
                put_text(104, 100, "CLEAR!", 3);
            if (game_state == ST_ANSWER && (frame_cnt & 0x10))
                put_text(16, 200, "DEMO", 3);
        }

        nmi_ready = 1;
    }
}

/* ---------------- input ---------------- */
static void read_pad(void)
{
    unsigned char i, b;

    pad1_prev = pad1;
    JOY1 = 1;
    JOY1 = 0;
    pad1 = 0;
    for (i = 0; i < 8; ++i) {
        b = JOY1 & 3;
        pad1 = (unsigned char)((pad1 << 1) | (b == 1 ? 1 : 0));
    }
    pad1_edge = (unsigned char)(pad1 & (unsigned char)~pad1_prev);
}

/* ---------------- title ---------------- */
static void update_title(void)
{
    if (pad1_edge & PAD_L) {
        if (level_id > 0)
            --level_id;
        else
            level_id = (unsigned char)(LEVEL_COUNT - 1);
        redraw_all = 1;
    }
    if (pad1_edge & PAD_R) {
        ++level_id;
        if (level_id >= LEVEL_COUNT)
            level_id = 0;
        redraw_all = 1;
    }
    if (pad1_edge & (PAD_START | PAD_A)) {
        load_level(level_id);
        game_state = ST_PLAY;
        redraw_all = 1;
    }
}

/* ---------------- play ---------------- */
static void update_play(void)
{
    signed char dx, dy;

    if (pad1_edge & PAD_START) {
        open_menu();
        return;
    }
    if (pad1_edge & PAD_SELECT) {
        reset_level();
        redraw_all = 1;
        sfx_reset();
        return;
    }
    if (pad1_edge & PAD_B) {
        undo_move();
        return;
    }

    dx = 0;
    dy = 0;
    if (pad1_edge & PAD_U) { dy = -1; }
    else if (pad1_edge & PAD_D) { dy = 1; }
    else if (pad1_edge & PAD_L) { dx = -1; }
    else if (pad1_edge & PAD_R) { dx = 1; }

    /* key repeat while held */
    if (dx == 0 && dy == 0) {
        if (pad1 & (PAD_U | PAD_D | PAD_L | PAD_R)) {
            if (hold_timer) {
                --hold_timer;
            } else {
                if (pad1 & PAD_U) dy = -1;
                else if (pad1 & PAD_D) dy = 1;
                else if (pad1 & PAD_L) dx = -1;
                else if (pad1 & PAD_R) dx = 1;
                hold_timer = 8;
            }
        } else {
            hold_timer = 12;
        }
    } else {
        hold_timer = 14;
    }

    if (dx || dy)
        try_move(dx, dy);
}

static void open_menu(void)
{
    menu_sel = MENU_RESET;
    menu_note = 0;
    game_state = ST_MENU;
    redraw_all = 1; /* black screen + menu text */
    sfx_move();
}

static void update_menu(void)
{
    if (pad1_edge & PAD_B) {
        menu_note = 0;
        game_state = ST_PLAY;
        redraw_all = 1; /* restore level */
        return;
    }
    if (pad1_edge & PAD_U) {
        if (menu_sel == 0)
            menu_sel = MENU_COUNT - 1;
        else
            --menu_sel;
        menu_note = 0;
        sfx_move();
    }
    if (pad1_edge & PAD_D) {
        ++menu_sel;
        if (menu_sel >= MENU_COUNT)
            menu_sel = 0;
        menu_note = 0;
        sfx_move();
    }
    if (pad1_edge & (PAD_A | PAD_START)) {
        if (menu_sel == MENU_RESET) {
            menu_note = 0;
            reset_level();
            game_state = ST_PLAY;
            redraw_all = 1;
            sfx_reset();
        } else if (menu_sel == MENU_NEXT) {
            menu_note = 0;
            ++level_id;
            if (level_id >= LEVEL_COUNT)
                level_id = 0;
            load_level(level_id);
            game_state = ST_PLAY;
            redraw_all = 1;
            sfx_move();
        } else {
            /* ANSWER */
            if (sol_length(level_id) == 0 || !sol_ptrs[level_id]) {
                sfx_block();
                menu_note = 1;
                redraw_all = 1; /* stay on menu, show NO ANSWER */
            } else {
                menu_note = 0;
                start_answer();
            }
        }
    }
}

static unsigned sol_length(unsigned char id)
{
    return (unsigned)sol_len_lo[id] | ((unsigned)sol_len_hi[id] << 8);
}

static void start_answer(void)
{
    /* load_level must not see ST_ANSWER yet (it would force ST_PLAY) */
    game_state = ST_PLAY;
    reset_level();
    sol_pos_lo = 0;
    sol_pos_hi = 0;
    sol_timer = 20; /* short pause before first step */
    game_state = ST_ANSWER;
    redraw_all = 1;
    sfx_push();
}

static void stop_answer(void)
{
    sol_pos_lo = 0;
    sol_pos_hi = 0;
    if (game_state == ST_ANSWER)
        game_state = ST_PLAY;
}

static void update_answer(void)
{
    unsigned pos, len;
    unsigned char step;
    signed char dx, dy;
    const unsigned char *sol;

    /* cancel */
    if (pad1_edge & (PAD_B | PAD_START | PAD_SELECT)) {
        stop_answer();
        return;
    }

    if (game_state == ST_WIN)
        return;

    if (sol_timer) {
        --sol_timer;
        return;
    }
    sol_timer = 5; /* playback speed */

    len = sol_length(level_id);
    pos = (unsigned)sol_pos_lo | ((unsigned)sol_pos_hi << 8);
    if (pos >= len || len == 0) {
        stop_answer();
        return;
    }

    sol = sol_ptrs[level_id];
    if (!sol) {
        stop_answer();
        return;
    }
    step = sol[pos];
    ++pos;
    sol_pos_lo = (unsigned char)(pos & 0xFF);
    sol_pos_hi = (unsigned char)((pos >> 8) & 0xFF);

    dx = 0;
    dy = 0;
    if (step == SOL_U) dy = -1;
    else if (step == SOL_D) dy = 1;
    else if (step == SOL_L) dx = -1;
    else if (step == SOL_R) dx = 1;
    else
        return;

    try_move(dx, dy);
}

static void update_win(void)
{
    if (pad1_edge & (PAD_START | PAD_A)) {
        ++level_id;
        if (level_id >= LEVEL_COUNT)
            level_id = 0;
        load_level(level_id);
        game_state = ST_PLAY;
        redraw_all = 1;
    }
    if (pad1_edge & PAD_B) {
        game_state = ST_TITLE;
        redraw_all = 1;
    }
}

/* ---------------- map helpers ---------------- */
static unsigned map_index(unsigned char x, unsigned char y)
{
    return (unsigned)y * (unsigned)map_w + (unsigned)x;
}

static unsigned char cell_at(unsigned char x, unsigned char y)
{
    if (x >= map_w || y >= map_h)
        return C_WALL;
    return map_cells[map_index(x, y)];
}

static void set_cell(unsigned char x, unsigned char y, unsigned char v)
{
    map_cells[map_index(x, y)] = v;
}

static unsigned char tile_for_cell(unsigned char c)
{
    if (c & C_WALL)
        return TILE_WALL;
    if (c & C_BOX)
        return (c & C_GOAL) ? TILE_BOXG : TILE_BOX;
    if (c & C_GOAL)
        return TILE_GOAL;
    return TILE_FLOOR;
}

/* ---------------- load / reset ---------------- */
static void load_level(unsigned char id)
{
    const unsigned char *src;
    unsigned i, n;
    unsigned char b, x, y, ch;
    unsigned char px, py;

    if (id >= LEVEL_COUNT)
        id = 0;
    level_id = id;

    map_w = level_w[id];
    map_h = level_h[id];
    src = level_ptrs[id];
    n = (unsigned)map_w * (unsigned)map_h;

    /* center on screen: 32x28 usable under 2-row HUD */
    off_x = (unsigned char)((32 - map_w) >> 1);
    off_y = (unsigned char)(2 + ((26 - map_h) >> 1));
    if (off_y < 2)
        off_y = 2;

    px = 0;
    py = 0;
    box_count = 0;

    for (i = 0; i < n; ++i) {
        /* packed: 2 cells per byte, high nibble first */
        if ((i & 1) == 0)
            b = src[i >> 1];
        ch = (i & 1) ? (unsigned char)(b & 0x0F) : (unsigned char)(b >> 4);

        x = (unsigned char)(i % map_w);
        y = (unsigned char)(i / map_w);

        /*
         * nibble encoding:
         * 0 empty  1 wall  2 goal  3 box  4 box+goal  5 player  6 player+goal
         */
        switch (ch) {
        case 1:
            map_cells[i] = C_WALL;
            break;
        case 2:
            map_cells[i] = C_GOAL;
            break;
        case 3:
            map_cells[i] = C_BOX;
            ++box_count;
            break;
        case 4:
            map_cells[i] = (unsigned char)(C_BOX | C_GOAL);
            ++box_count;
            break;
        case 5:
            map_cells[i] = 0;
            px = x;
            py = y;
            break;
        case 6:
            map_cells[i] = C_GOAL;
            px = x;
            py = y;
            break;
        default:
            map_cells[i] = 0;
            break;
        }
    }

    player_x = px;
    player_y = py;
    moves_lo = 0;
    moves_hi = 0;
    hist_len = 0;
    dirty_n = 0;
    hold_timer = 0;
    goal_ok = 0;
    sol_pos_lo = 0;
    sol_pos_hi = 0;
    hud_dirty = 1;
    check_win(); /* just compute goal_ok without switching state */
    if (game_state == ST_WIN)
        game_state = ST_PLAY;
}

static void reset_level(void)
{
    load_level(level_id);
}

/* ---------------- move / undo (same rules as html_app) ---------------- */
static void try_move(signed char dx, signed char dy)
{
    unsigned char nx, ny, bx, by;
    unsigned char c, c2;

    nx = (unsigned char)(player_x + dx);
    ny = (unsigned char)(player_y + dy);
    c = cell_at(nx, ny);

    if (c & C_WALL) {
        sfx_block();
        return;
    }

    if (c & C_BOX) {
        bx = (unsigned char)(nx + dx);
        by = (unsigned char)(ny + dy);
        c2 = cell_at(bx, by);
        if ((c2 & C_WALL) || (c2 & C_BOX)) {
            sfx_block();
            return;
        }

        /* push box */
        if (hist_len < HIST_MAX) {
            hist_px[hist_len] = player_x;
            hist_py[hist_len] = player_y;
            hist_flag[hist_len] = 1;
            hist_bx[hist_len] = bx;
            hist_by[hist_len] = by;
            ++hist_len;
        }

        /* clear box from nx,ny; add to bx,by */
        set_cell(nx, ny, (unsigned char)(c & (unsigned char)~C_BOX));
        set_cell(bx, by, (unsigned char)(c2 | C_BOX));
        mark_dirty(nx, ny);
        mark_dirty(bx, by);

        player_x = nx;
        player_y = ny;

        ++moves_lo;
        if (moves_lo == 0)
            ++moves_hi;
        hud_dirty = 1;

        sfx_push();
        check_win();
        return;
    }

    /* walk (no step count, same as html_app) */
    if (hist_len < HIST_MAX) {
        hist_px[hist_len] = player_x;
        hist_py[hist_len] = player_y;
        hist_flag[hist_len] = 0;
        ++hist_len;
    }
    player_x = nx;
    player_y = ny;
    sfx_move();
}

static void undo_move(void)
{
    unsigned char f, px, py, bx, by, fromx, fromy;
    unsigned char c, c2;

    if (hist_len == 0)
        return;

    /* like html_app: skip pure walks until a push, or undo walks */
    while (hist_len > 0) {
        --hist_len;
        f = hist_flag[hist_len];
        px = hist_px[hist_len];
        py = hist_py[hist_len];

        if (!f) {
            player_x = px;
            player_y = py;
            /* continue if we want push-only undo — html pops walks then one push */
            /* Keep same: undo all walks until push, then undo that push */
            continue;
        }

        /* undo push: box currently at hist_bx/by, was at player pos after push = old front */
        bx = hist_bx[hist_len];
        by = hist_by[hist_len];
        /* after push, player is at the cell the box left; that cell is not stored —
         * box came from (player position before undo's restore, which is current player) */
        fromx = player_x;
        fromy = player_y;

        c = cell_at(bx, by);
        c2 = cell_at(fromx, fromy);
        set_cell(bx, by, (unsigned char)(c & (unsigned char)~C_BOX));
        set_cell(fromx, fromy, (unsigned char)(c2 | C_BOX));
        mark_dirty(bx, by);
        mark_dirty(fromx, fromy);

        player_x = px;
        player_y = py;

        if (moves_lo == 0) {
            if (moves_hi) {
                --moves_hi;
                moves_lo = 255;
            }
        } else {
            --moves_lo;
        }
        hud_dirty = 1;

        sfx_undo();
        goal_ok = 0;
        if (game_state != ST_ANSWER)
            game_state = ST_PLAY;
        check_win();
        return;
    }
    /* only walks undone */
    sfx_undo();
}

static void check_win(void)
{
    unsigned i, n;
    unsigned char c, boxes, on_goal;

    n = (unsigned)map_w * (unsigned)map_h;
    boxes = 0;
    on_goal = 0;
    for (i = 0; i < n; ++i) {
        c = map_cells[i];
        if (c & C_BOX) {
            ++boxes;
            if (c & C_GOAL)
                ++on_goal;
        }
    }
    box_count = boxes;
    goal_ok = on_goal;
    hud_dirty = 1;
    if (boxes > 0 && boxes == on_goal) {
        if (game_state == ST_PLAY || game_state == ST_ANSWER) {
            game_state = ST_WIN;
            sfx_win();
        }
    }
}

/* ---------------- dirty VRAM ---------------- */
static void mark_dirty(unsigned char x, unsigned char y)
{
    if (dirty_n >= DIRTY_MAX)
        return;
    dirty_x[dirty_n] = x;
    dirty_y[dirty_n] = y;
    ++dirty_n;
}

static void apply_dirty(void)
{
    unsigned char i, x, y, tx, ty, t;

    for (i = 0; i < dirty_n; ++i) {
        x = dirty_x[i];
        y = dirty_y[i];
        tx = (unsigned char)(off_x + x);
        ty = (unsigned char)(off_y + y);
        t = tile_for_cell(cell_at(x, y));
        poke_bg_tile(tx, ty, t);
    }
    dirty_n = 0;
}

static void poke_bg_tile(unsigned char tx, unsigned char ty, unsigned char tile)
{
    unsigned hi, lo;

    (void)PPUSTATUS;
    /* nametable 0: $2000 + ty*32 + tx */
    hi = 0x20;
    lo = (unsigned)(ty << 5) + tx;
    hi += (lo >> 8);
    lo &= 0xFF;
    PPUADDR = (unsigned char)hi;
    PPUADDR = (unsigned char)lo;
    PPUDATA = tile;
}

/* ---------------- draw ---------------- */
static void clear_oam(void)
{
    unsigned i;
    for (i = 0; i < 256; ++i)
        oam[i] = 0xFF;
    oam_idx = 0;
}

static void put_spr(unsigned char y, unsigned char tile, unsigned char attr, unsigned char x)
{
    unsigned char i = oam_idx;
    if (i >= 252)
        return;
    oam[i++] = y;
    oam[i++] = tile;
    oam[i++] = attr;
    oam[i++] = x;
    oam_idx = i;
}

/* Map ASCII to sprite font tile */
static unsigned char char_to_spr(char c)
{
    if (c >= 'a' && c <= 'z')
        c = (char)(c - 32);
    if (c >= 'A' && c <= 'Z')
        return (unsigned char)(SPR_A + (c - 'A'));
    if (c >= '0' && c <= '9')
        return (unsigned char)(SPR_DIGIT0 + (c - '0'));
    if (c == '>')
        return SPR_GT;
    if (c == '/')
        return 0x2F;
    if (c == '-')
        return 0x2D;
    if (c == ':')
        return 0x3A;
    return SPR_SPACE;
}

/* Map ASCII to BG font tile (nametable) */
static unsigned char char_to_bg(char c)
{
    if (c >= 'a' && c <= 'z')
        c = (char)(c - 32);
    if (c >= 'A' && c <= 'Z')
        return (unsigned char)(0x41 + (c - 'A'));
    if (c >= '0' && c <= '9')
        return (unsigned char)(0x30 + (c - '0'));
    if (c == '/')
        return 0x2F;
    if (c == ':')
        return 0x3A;
    if (c == '-')
        return 0x2D;
    if (c == '>')
        return 0x3E;
    if (c == '!')
        return 0x21;
    return 0; /* blank / black */
}

static void put_text(unsigned char y, unsigned char x, const char *s, unsigned char attr)
{
    while (*s) {
        put_spr(y, char_to_spr(*s), attr, x);
        x = (unsigned char)(x + 8);
        ++s;
    }
}

static void put_bg_char(unsigned char tx, unsigned char ty, char ch)
{
    poke_bg_tile(tx, ty, char_to_bg(ch));
}

static void put_bg_str(unsigned char tx, unsigned char ty, const char *s)
{
    while (*s) {
        put_bg_char(tx, ty, *s);
        ++tx;
        ++s;
    }
}

static void put_bg_num2(unsigned char tx, unsigned char ty, unsigned char n)
{
    put_bg_char(tx, ty, (char)('0' + (n / 10) % 10));
    put_bg_char((unsigned char)(tx + 1), ty, (char)('0' + (n % 10)));
}

static void put_bg_num3(unsigned char tx, unsigned char ty, unsigned lo, unsigned char hi)
{
    unsigned v = lo + ((unsigned)hi << 8);
    unsigned char d0, d1, d2;
    d0 = (unsigned char)(v % 10);
    v /= 10;
    d1 = (unsigned char)(v % 10);
    v /= 10;
    d2 = (unsigned char)(v % 10);
    put_bg_char(tx, ty, (char)('0' + d2));
    put_bg_char((unsigned char)(tx + 1), ty, (char)('0' + d1));
    put_bg_char((unsigned char)(tx + 2), ty, (char)('0' + d0));
}

static void draw_sprites(void)
{
    unsigned char sx, sy;

    sx = (unsigned char)((off_x + player_x) << 3);
    sy = (unsigned char)(((off_y + player_y) << 3) - 1);
    put_spr(sy, SPR_PLAYER, 0, sx);
}

/* HUD as background tiles — avoids 8-sprites-per-line limit */
static void draw_hud_bg(void)
{
    unsigned char i, lv;

    for (i = 0; i < 32; ++i)
        poke_bg_tile(i, 0, TILE_HUD);

    lv = (unsigned char)(level_id + 1);
    put_bg_str(1, 0, "L");
    put_bg_num2(2, 0, lv);
    put_bg_str(5, 0, "M");
    put_bg_num3(6, 0, moves_lo, moves_hi);
    put_bg_str(10, 0, "B");
    put_bg_num2(11, 0, goal_ok);
    put_bg_char(13, 0, '/');
    put_bg_num2(14, 0, box_count);
}

/* Pure black menu + English labels on BG */
static void draw_menu_screen(void)
{
    unsigned char i;

    clear_nametable();

    /* all black attrs (palette 0, color0 backdrop) */
    (void)PPUSTATUS;
    PPUADDR = 0x23;
    PPUADDR = 0xC0;
    for (i = 0; i < 64; ++i)
        PPUDATA = 0x00;

    put_bg_str(13, 8, "MENU");
    put_bg_str(12, 12, "RESET");
    put_bg_str(12, 14, "NEXT");
    put_bg_str(12, 16, "ANSWER");
    put_bg_str(8, 20, "A:OK  B:BACK");
    if (menu_note)
        put_bg_str(11, 22, "NO ANSWER");

    PPUSCROLL = 0;
    PPUSCROLL = 0;
}

static void draw_menu_cursor(void)
{
    /* yellow > next to selected item; items at rows 12,14,16 → y = row*8-1 */
    unsigned char row = (unsigned char)(12 + menu_sel * 2);
    unsigned char y = (unsigned char)((row << 3) - 1);
    put_spr(y, SPR_GT, 3, 80); /* col 10 * 8 */
}

static void draw_title(void)
{
    unsigned char x, y, i;

    clear_nametable();

    /* blue floor frame */
    for (y = 0; y < 30; ++y) {
        for (x = 0; x < 32; ++x)
            poke_bg_tile(x, y, TILE_FLOOR);
    }
    /* black center for text */
    for (y = 6; y < 22; ++y) {
        for (x = 6; x < 26; ++x)
            poke_bg_tile(x, y, 0);
    }

    put_bg_str(12, 8, "SOKOBAN");
    put_bg_str(10, 12, "PRESS START");
    put_bg_str(11, 16, "LEVEL");
    put_bg_num2(17, 16, (unsigned char)(level_id + 1));
    put_bg_str(8, 20, "LEFT RIGHT SEL");

    /* title uses floor palette (blue) + black holes */
    (void)PPUSTATUS;
    PPUADDR = 0x23;
    PPUADDR = 0xC0;
    for (i = 0; i < 64; ++i)
        PPUDATA = 0x00;

    PPUSCROLL = 0;
    PPUSCROLL = 0;
}

static void draw_title_sprites(void)
{
    /* title text is BG; no sprites needed */
}

static void draw_level_full(void)
{
    unsigned char x, y, tx, ty, t;

    clear_nametable();

    for (y = 0; y < map_h; ++y) {
        for (x = 0; x < map_w; ++x) {
            tx = (unsigned char)(off_x + x);
            ty = (unsigned char)(off_y + y);
            t = tile_for_cell(cell_at(x, y));
            poke_bg_tile(tx, ty, t);
        }
    }
    draw_hud_bg();
    fill_level_attr();
    PPUSCROLL = 0;
    PPUSCROLL = 0;
}

static void clear_nametable(void)
{
    unsigned i;

    (void)PPUSTATUS;
    PPUADDR = 0x20;
    PPUADDR = 0x00;
    for (i = 0; i < 1024; ++i)
        PPUDATA = 0;
}

/* Single BG palette for whole map — same type always same color */
static void fill_level_attr(void)
{
    unsigned char i;

    (void)PPUSTATUS;
    PPUADDR = 0x23;
    PPUADDR = 0xC0;
    for (i = 0; i < 64; ++i)
        PPUDATA = 0x00;
}

static void wait_vblank(void)
{
    while (PPUSTATUS & 0x80)
        ;
    while (!(PPUSTATUS & 0x80))
        ;
}
