#include "game.h"
#include "gfx.h"
#include "levels.h"
#include "sound.h"

Game g;

static void load_level(u8 id);
static void try_move(s8 dx, s8 dy);
static void undo_move(void);
static void check_win(void);
static void update_cam(void);
static u8 cell_at(u8 x, u8 y);
static void set_cell(u8 x, u8 y, u8 v);
static void draw_play(void);
static void draw_title(void);
static void draw_menu(void);
static void draw_hud(void);
static void num_to_str(char *buf, u16 n, int digits);

void game_init(void)
{
	g.state = ST_TITLE;
	g.level_id = 0;
	g.need_redraw = 1;
	g.menu_sel = 0;
	g.menu_note = 0;
	g.hold_t = 0;
	g.hold_key = 0;
}

static u16 map_index(u8 x, u8 y)
{
	return (u16)y * g.map_w + x;
}

static u8 cell_at(u8 x, u8 y)
{
	if (x >= g.map_w || y >= g.map_h)
		return C_WALL;
	return g.cells[map_index(x, y)];
}

static void set_cell(u8 x, u8 y, u8 v)
{
	g.cells[map_index(x, y)] = v;
}

static void load_level(u8 id)
{
	const u8 *src;
	u16 i, n;
	u8 b = 0, ch, x, y;
	u8 ppx = 0, ppy = 0;

	if (id >= LEVEL_COUNT)
		id = 0;
	g.level_id = id;
	g.map_w = level_w[id];
	g.map_h = level_h[id];
	src = level_ptrs[id];
	n = (u16)g.map_w * g.map_h;
	g.box_count = 0;

	for (i = 0; i < n; i++) {
		if ((i & 1) == 0)
			b = src[i >> 1];
		ch = (i & 1) ? (u8)(b & 0x0F) : (u8)(b >> 4);
		x = (u8)(i % g.map_w);
		y = (u8)(i / g.map_w);
		switch (ch) {
		case 1:
			g.cells[i] = C_WALL;
			break;
		case 2:
			g.cells[i] = C_GOAL;
			break;
		case 3:
			g.cells[i] = C_BOX;
			g.box_count++;
			break;
		case 4:
			g.cells[i] = (u8)(C_BOX | C_GOAL);
			g.box_count++;
			break;
		case 5:
			g.cells[i] = 0;
			ppx = x;
			ppy = y;
			break;
		case 6:
			g.cells[i] = C_GOAL;
			ppx = x;
			ppy = y;
			break;
		default:
			g.cells[i] = 0;
			break;
		}
	}
	g.px = ppx;
	g.py = ppy;
	g.moves = 0;
	g.hist_len = 0;
	g.sol_pos = 0;
	g.sol_timer = 0;
	g.goal_ok = 0;
	check_win();
	if (g.state == ST_WIN)
		g.state = ST_PLAY;
	update_cam();
	g.need_redraw = 1;
}

static void update_cam(void)
{
	int view_w = SCREEN_W / CELL;
	int view_h = VIEW_H / CELL;
	int cx = (int)g.px - view_w / 2;
	int cy = (int)g.py - view_h / 2;
	int max_x = (int)g.map_w - view_w;
	int max_y = (int)g.map_h - view_h;
	if (max_x < 0)
		max_x = 0;
	if (max_y < 0)
		max_y = 0;
	if (cx < 0)
		cx = 0;
	if (cy < 0)
		cy = 0;
	if (cx > max_x)
		cx = max_x;
	if (cy > max_y)
		cy = max_y;
	/* center small maps */
	if (g.map_w * CELL < SCREEN_W)
		g.cam_x = 0;
	else
		g.cam_x = (u8)cx;
	if (g.map_h * CELL < VIEW_H)
		g.cam_y = 0;
	else
		g.cam_y = (u8)cy;
}

static void try_move(s8 dx, s8 dy)
{
	u8 nx, ny, bx, by, c, c2;

	nx = (u8)(g.px + dx);
	ny = (u8)(g.py + dy);
	c = cell_at(nx, ny);
	if (c & C_WALL) {
		sfx_block();
		return;
	}
	if (c & C_BOX) {
		bx = (u8)(nx + dx);
		by = (u8)(ny + dy);
		c2 = cell_at(bx, by);
		if ((c2 & C_WALL) || (c2 & C_BOX)) {
			sfx_block();
			return;
		}
		if (g.hist_len < HIST_MAX) {
			g.hist_px[g.hist_len] = g.px;
			g.hist_py[g.hist_len] = g.py;
			g.hist_flag[g.hist_len] = 1;
			g.hist_bx[g.hist_len] = bx;
			g.hist_by[g.hist_len] = by;
			g.hist_len++;
		}
		set_cell(nx, ny, (u8)(c & (u8)~C_BOX));
		set_cell(bx, by, (u8)(c2 | C_BOX));
		g.px = nx;
		g.py = ny;
		g.moves++;
		sfx_push();
		update_cam();
		check_win();
		g.need_redraw = 1;
		return;
	}
	if (g.hist_len < HIST_MAX) {
		g.hist_px[g.hist_len] = g.px;
		g.hist_py[g.hist_len] = g.py;
		g.hist_flag[g.hist_len] = 0;
		g.hist_len++;
	}
	g.px = nx;
	g.py = ny;
	sfx_move();
	update_cam();
	g.need_redraw = 1;
}

static void undo_move(void)
{
	u8 f, px, py, bx, by, fromx, fromy, c, c2;

	if (g.hist_len == 0)
		return;
	while (g.hist_len > 0) {
		g.hist_len--;
		f = g.hist_flag[g.hist_len];
		px = g.hist_px[g.hist_len];
		py = g.hist_py[g.hist_len];
		if (!f) {
			g.px = px;
			g.py = py;
			continue;
		}
		bx = g.hist_bx[g.hist_len];
		by = g.hist_by[g.hist_len];
		fromx = g.px;
		fromy = g.py;
		c = cell_at(bx, by);
		c2 = cell_at(fromx, fromy);
		set_cell(bx, by, (u8)(c & (u8)~C_BOX));
		set_cell(fromx, fromy, (u8)(c2 | C_BOX));
		g.px = px;
		g.py = py;
		if (g.moves)
			g.moves--;
		sfx_undo();
		if (g.state != ST_ANSWER)
			g.state = ST_PLAY;
		update_cam();
		check_win();
		g.need_redraw = 1;
		return;
	}
	update_cam();
	g.need_redraw = 1;
	sfx_undo();
}

static void check_win(void)
{
	u16 i, n = (u16)g.map_w * g.map_h;
	u8 boxes = 0, on = 0, c;
	for (i = 0; i < n; i++) {
		c = g.cells[i];
		if (c & C_BOX) {
			boxes++;
			if (c & C_GOAL)
				on++;
		}
	}
	g.box_count = boxes;
	g.goal_ok = on;
	if (boxes > 0 && boxes == on) {
		if (g.state == ST_PLAY || g.state == ST_ANSWER) {
			g.state = ST_WIN;
			sfx_win();
			g.need_redraw = 1;
		}
	}
}

static void start_answer(void)
{
	if (sol_len[g.level_id] == 0 || !sol_ptrs[g.level_id]) {
		g.menu_note = 1;
		sfx_block();
		g.need_redraw = 1;
		return;
	}
	g.state = ST_PLAY;
	load_level(g.level_id);
	g.sol_pos = 0;
	g.sol_timer = 20;
	g.state = ST_ANSWER;
	g.need_redraw = 1;
	sfx_menu();
}

void game_update(u16 keys, u16 pressed)
{
	s8 dx = 0, dy = 0;

	(void)keys;

	if (g.state == ST_TITLE) {
		if (pressed & KEY_LEFT) {
			if (g.level_id == 0)
				g.level_id = (u8)(LEVEL_COUNT - 1);
			else
				g.level_id--;
			g.need_redraw = 1;
			sfx_menu();
		}
		if (pressed & KEY_RIGHT) {
			g.level_id++;
			if (g.level_id >= LEVEL_COUNT)
				g.level_id = 0;
			g.need_redraw = 1;
			sfx_menu();
		}
		if (pressed & (KEY_START | KEY_A)) {
			load_level(g.level_id);
			g.state = ST_PLAY;
			g.need_redraw = 1;
			sfx_menu();
		}
		return;
	}

	if (g.state == ST_MENU) {
		if (pressed & KEY_B) {
			g.state = ST_PLAY;
			g.menu_note = 0;
			g.need_redraw = 1;
			return;
		}
		if (pressed & KEY_UP) {
			if (g.menu_sel == 0)
				g.menu_sel = MENU_COUNT - 1;
			else
				g.menu_sel--;
			g.menu_note = 0;
			sfx_menu();
			g.need_redraw = 1;
		}
		if (pressed & KEY_DOWN) {
			g.menu_sel++;
			if (g.menu_sel >= MENU_COUNT)
				g.menu_sel = 0;
			g.menu_note = 0;
			sfx_menu();
			g.need_redraw = 1;
		}
		if (pressed & (KEY_A | KEY_START)) {
			if (g.menu_sel == MENU_RESET) {
				load_level(g.level_id);
				g.state = ST_PLAY;
				sfx_menu();
			} else if (g.menu_sel == MENU_NEXT) {
				g.level_id++;
				if (g.level_id >= LEVEL_COUNT)
					g.level_id = 0;
				load_level(g.level_id);
				g.state = ST_PLAY;
				sfx_menu();
			} else {
				start_answer();
			}
			g.need_redraw = 1;
		}
		return;
	}

	if (g.state == ST_WIN) {
		if (pressed & (KEY_START | KEY_A)) {
			g.level_id++;
			if (g.level_id >= LEVEL_COUNT)
				g.level_id = 0;
			load_level(g.level_id);
			g.state = ST_PLAY;
			g.need_redraw = 1;
		}
		if (pressed & KEY_B) {
			g.state = ST_TITLE;
			g.need_redraw = 1;
		}
		return;
	}

	if (g.state == ST_ANSWER) {
		if (pressed & (KEY_B | KEY_START | KEY_SELECT)) {
			g.state = ST_PLAY;
			g.need_redraw = 1;
			return;
		}
		if (g.sol_timer) {
			g.sol_timer--;
			return;
		}
		g.sol_timer = 4;
		if (g.sol_pos >= sol_len[g.level_id]) {
			g.state = ST_PLAY;
			return;
		}
		{
			u8 step = sol_ptrs[g.level_id][g.sol_pos++];
			dx = dy = 0;
			if (step == SOL_U)
				dy = -1;
			else if (step == SOL_D)
				dy = 1;
			else if (step == SOL_L)
				dx = -1;
			else if (step == SOL_R)
				dx = 1;
			if (dx || dy)
				try_move(dx, dy);
		}
		return;
	}

	/* PLAY */
	if (pressed & KEY_START) {
		g.menu_sel = 0;
		g.menu_note = 0;
		g.state = ST_MENU;
		g.need_redraw = 1;
		sfx_menu();
		return;
	}
	if (pressed & KEY_SELECT) {
		load_level(g.level_id);
		sfx_menu();
		return;
	}
	if (pressed & KEY_B) {
		undo_move();
		return;
	}

	if (pressed & KEY_UP)
		dy = -1;
	else if (pressed & KEY_DOWN)
		dy = 1;
	else if (pressed & KEY_LEFT)
		dx = -1;
	else if (pressed & KEY_RIGHT)
		dx = 1;

	if (dx || dy)
		try_move(dx, dy);
}

static void num_to_str(char *buf, u16 n, int digits)
{
	int i;
	for (i = digits - 1; i >= 0; i--) {
		buf[i] = (char)('0' + (n % 10));
		n /= 10;
	}
	buf[digits] = 0;
}

static void draw_hud(void)
{
	char buf[8];
	int i;
	/* top bar */
	for (i = 0; i < SCREEN_W / CELL; i++)
		gfx_blit_tile(i * CELL, 0, TIL_HUD);
	/* fill remainder */
	gfx_fill((SCREEN_W / CELL) * CELL, 0, SCREEN_W % CELL, HUD_H, RGB15(4, 6, 12));

	gfx_text_shadow(4, 4, "LV", RGB15(28, 28, 20), RGB15(2, 2, 4));
	num_to_str(buf, (u16)(g.level_id + 1), 2);
	gfx_text_shadow(18, 4, buf, RGB15(31, 31, 28), RGB15(2, 2, 4));

	gfx_text_shadow(40, 4, "MOV", RGB15(20, 24, 28), RGB15(2, 2, 4));
	num_to_str(buf, g.moves, 3);
	gfx_text_shadow(60, 4, buf, RGB15(31, 31, 28), RGB15(2, 2, 4));

	gfx_text_shadow(90, 4, "BOX", RGB15(28, 20, 10), RGB15(2, 2, 4));
	num_to_str(buf, g.goal_ok, 2);
	gfx_text_shadow(110, 4, buf, RGB15(31, 28, 10), RGB15(2, 2, 4));
	gfx_text_shadow(122, 4, "/", RGB15(20, 20, 24), RGB15(2, 2, 4));
	num_to_str(buf, g.box_count, 2);
	gfx_text_shadow(128, 4, buf, RGB15(31, 28, 10), RGB15(2, 2, 4));

	if (g.state == ST_ANSWER)
		gfx_text_shadow(160, 4, "DEMO", RGB15(31, 28, 8), RGB15(4, 2, 0));
	if (g.state == ST_WIN)
		gfx_text_shadow(160, 4, "CLEAR!", RGB15(10, 31, 12), RGB15(0, 4, 0));
}

static void draw_play(void)
{
	int x, y, tid;
	u8 c;
	int off_px = 0, off_py = HUD_H;

	/* center small maps */
	if (g.map_w * CELL < SCREEN_W)
		off_px = (SCREEN_W - g.map_w * CELL) / 2;
	if (g.map_h * CELL < VIEW_H)
		off_py = HUD_H + (VIEW_H - g.map_h * CELL) / 2;

	gfx_clear(RGB15(2, 2, 4));
	draw_hud();

	for (y = 0; y < g.map_h; y++) {
		for (x = 0; x < g.map_w; x++) {
			int sx = off_px + (x - g.cam_x) * CELL;
			int sy = off_py + (y - g.cam_y) * CELL;
			if (sx + CELL <= 0 || sy + CELL <= HUD_H)
				continue;
			if (sx >= SCREEN_W || sy >= SCREEN_H)
				continue;
			c = cell_at((u8)x, (u8)y);
			if (c & C_WALL)
				tid = TIL_WALL;
			else if (c & C_BOX)
				tid = (c & C_GOAL) ? TIL_BOXG : TIL_BOX;
			else if (c & C_GOAL)
				tid = TIL_GOAL;
			else
				tid = TIL_FLOOR;
			gfx_blit_tile(sx, sy, tid);
		}
	}

	/* player on top */
	{
		int sx = off_px + (g.px - g.cam_x) * CELL;
		int sy = off_py + (g.py - g.cam_y) * CELL;
		gfx_blit_tile_key(sx, sy, TIL_PLAYER, 0);
	}

	if (g.state == ST_WIN) {
		gfx_fill(50, 70, 140, 28, RGB15(4, 8, 4));
		gfx_text_shadow(78, 78, "LEVEL CLEAR!", RGB15(12, 31, 14), RGB15(0, 4, 0));
		gfx_text_shadow(62, 100, "A:NEXT  B:TITLE", RGB15(24, 28, 20), RGB15(2, 2, 2));
	}
}

static void draw_title(void)
{
	char buf[8];
	int i, j;
	gfx_clear(RGB15(3, 5, 12));
	/* decorative border */
	for (i = 0; i < SCREEN_W / CELL; i++) {
		gfx_blit_tile(i * CELL, 0, TIL_PANEL);
		gfx_blit_tile(i * CELL, SCREEN_H - CELL, TIL_PANEL);
	}
	for (j = 1; j < SCREEN_H / CELL - 1; j++) {
		gfx_blit_tile(0, j * CELL, TIL_PANEL);
		gfx_blit_tile(SCREEN_W - CELL, j * CELL, TIL_PANEL);
	}
	/* sample tiles showcase */
	gfx_blit_tile(48, 40, TIL_WALL);
	gfx_blit_tile(64, 40, TIL_FLOOR);
	gfx_blit_tile(80, 40, TIL_GOAL);
	gfx_blit_tile(96, 40, TIL_BOX);
	gfx_blit_tile(112, 40, TIL_BOXG);
	gfx_blit_tile_key(128, 40, TIL_PLAYER, 0);

	gfx_text_shadow(78, 64, "SOKOBAN", RGB15(31, 28, 12), RGB15(4, 2, 0));
	gfx_text_shadow(58, 84, "PRESS START", RGB15(24, 28, 31), RGB15(2, 2, 6));
	gfx_text_shadow(70, 104, "LEVEL", RGB15(18, 22, 28), RGB15(2, 2, 4));
	num_to_str(buf, (u16)(g.level_id + 1), 2);
	gfx_text_shadow(108, 104, buf, RGB15(31, 31, 28), RGB15(2, 2, 4));
	gfx_text_shadow(40, 124, "LEFT RIGHT SELECT", RGB15(14, 18, 24), RGB15(2, 2, 4));
	gfx_text_shadow(34, 140, "GBA HD REMAKE", RGB15(10, 16, 22), RGB15(1, 1, 2));
}

static void draw_menu(void)
{
	const char *items[3] = {"RESET", "NEXT", "ANSWER"};
	int i;
	/* dim playfield then panel */
	draw_play();
	gfx_fill(40, 36, 160, 100, RGB15(2, 4, 10));
	/* border */
	gfx_fill(40, 36, 160, 2, RGB15(14, 18, 28));
	gfx_fill(40, 134, 160, 2, RGB15(14, 18, 28));
	gfx_fill(40, 36, 2, 100, RGB15(14, 18, 28));
	gfx_fill(198, 36, 2, 100, RGB15(14, 18, 28));

	gfx_text_shadow(100, 44, "MENU", RGB15(31, 28, 14), RGB15(4, 2, 0));
	for (i = 0; i < MENU_COUNT; i++) {
		u16 col = (i == g.menu_sel) ? RGB15(31, 31, 20) : RGB15(16, 20, 26);
		if (i == g.menu_sel)
			gfx_text_shadow(70, 64 + i * 16, ">", RGB15(31, 24, 8), RGB15(4, 2, 0));
		gfx_text_shadow(84, 64 + i * 16, items[i], col, RGB15(2, 2, 4));
	}
	if (g.menu_note)
		gfx_text_shadow(78, 116, "NO ANSWER", RGB15(31, 10, 10), RGB15(6, 0, 0));
	else
		gfx_text_shadow(60, 116, "A:OK  B:BACK", RGB15(12, 16, 22), RGB15(2, 2, 4));
}

void game_draw(void)
{
	if (g.state == ST_TITLE)
		draw_title();
	else if (g.state == ST_MENU)
		draw_menu();
	else
		draw_play();
	g.need_redraw = 0;
}
