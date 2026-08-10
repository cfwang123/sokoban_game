/* Self-test: exercise sk_try_move sequences; exit 0 on pass */
#include "game.h"
#include <stdio.h>
#include <string.h>

static int expect_pos(const SkGame *g, int x, int y, const char *tag)
{
    if (g->px != x || g->py != y) {
        fprintf(stderr, "FAIL %s: pos=(%d,%d) want=(%d,%d)\n", tag, g->px, g->py, x, y);
        return 0;
    }
    return 1;
}

static int expect_cell(const SkGame *g, int x, int y, int ch, const char *tag)
{
    int c = sk_cell(g, x, y);
    if (c != ch) {
        fprintf(stderr, "FAIL %s: cell(%d,%d)='%c'(%d) want='%c'\n", tag, x, y, c, c, ch);
        return 0;
    }
    return 1;
}

int main(void)
{
    SkGame g;
    int ok = 1;

    sk_reset(&g);
    ok &= expect_pos(&g, 3, 3, "reset");
    ok &= expect_cell(&g, 3, 3, '@', "player");

    /* wall */
    if (sk_try_move(&g, 0, -3) != 0) {
        fprintf(stderr, "FAIL wall should fail\n");
        ok = 0;
    }

    /* walk left onto goal area: from (3,3) left is $ box */
    /* right: (4,3) is $ — push right into . → * */
    if (sk_try_move(&g, 1, 0) != 1) {
        fprintf(stderr, "FAIL push right\n");
        ok = 0;
    }
    ok &= expect_pos(&g, 4, 3, "after push r");
    ok &= expect_cell(&g, 5, 3, '*', "box on goal");
    if (g.moves != 1) {
        fprintf(stderr, "FAIL moves=%d want 1\n", g.moves);
        ok = 0;
    }

    /* from (4,3) walk left onto floor (box was pushed away) */
    if (sk_try_move(&g, -1, 0) != 1) {
        fprintf(stderr, "FAIL walk left\n");
        ok = 0;
    }
    ok &= expect_pos(&g, 3, 3, "after walk l");
    if (g.moves != 1) {
        fprintf(stderr, "FAIL moves should stay 1 after walk, got %d\n", g.moves);
        ok = 0;
    }

    /* sk_undo replays through pure walks until a push (or empty) */
    sk_undo(&g);
    ok &= expect_pos(&g, 3, 3, "undo to before push");
    ok &= expect_cell(&g, 4, 3, '$', "box restored");
    if (g.moves != 0) {
        fprintf(stderr, "FAIL moves after undo=%d\n", g.moves);
        ok = 0;
    }

    /* blocked push into wall upward from start: up is $ then # */
    sk_reset(&g);
    if (sk_try_move(&g, 0, -1) != 1) { /* push up $ into space row2 */
        /* map row2 is # $$$ # — from (3,3) up is (3,2) which is $ */
        fprintf(stderr, "note: up from start\n");
    }
    /* From (3,3) dy=-1: cell is $ (row2 col3). Ahead (3,1) is space. Should push. */
    sk_reset(&g);
    if (sk_try_move(&g, 0, -1) != 1) {
        fprintf(stderr, "FAIL push up\n");
        ok = 0;
    }
    ok &= expect_pos(&g, 3, 2, "after push up");

    if (ok) {
        puts("PASS");
        return 0;
    }
    puts("FAIL");
    return 1;
}
