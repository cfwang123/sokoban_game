#ifndef WQX_UI_H
#define WQX_UI_H

#include "game.h"

/** 整帧绘制：状态栏 + 棋盘 + 软键提示。 */
void ui_draw(const GameState *s, const char *status);

/** 通关条幅。 */
void ui_draw_win(const GameState *s);

#endif
