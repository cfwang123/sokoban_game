/**
 * gtkapp1 — GTK3 推箱子（教学演示源码）
 * 不要求在本仓库内编译。Linux 可选：
 *   gcc -O2 main.c game.c -o sokoban `pkg-config --cflags --libs gtk+-3.0`
 *
 * 键位：WASD / 方向键，Z 撤销，R 重置，Q/Esc 退出
 *
 * 注：用户提到的 “gtx” 按 GTK 理解；NVIDIA GTX 显卡无关。
 */
#include <gtk/gtk.h>
#include <string.h>
#include "game.h"

#define CELL 40
#define PAD  16

static GameState g;
static const char *LEVEL[] = {
    "#######", "#. . .#", "# $$$ #", "#.$@$.#",
    "# $$$ #", "#. . .#", "#######",
};

static void load(void) { game_from_rows(&g, LEVEL, 7); }

static gboolean on_draw(GtkWidget *widget, cairo_t *cr, gpointer data)
{
    int x, y;
    char status[80];
    (void)widget;
    (void)data;

    cairo_set_source_rgb(cr, 0.10, 0.10, 0.18);
    cairo_paint(cr);

    for (y = 0; y < g.height; y++) {
        for (x = 0; x < g.width; x++) {
            double rx = PAD + x * CELL;
            double ry = PAD + y * CELL;
            char ch = g.map[x][y];
            if (ch == '#') {
                cairo_set_source_rgb(cr, 0.29, 0.29, 0.41);
                cairo_rectangle(cr, rx, ry, CELL, CELL);
                cairo_fill(cr);
            } else {
                cairo_set_source_rgb(cr, 0.23, 0.23, 0.33);
                cairo_rectangle(cr, rx, ry, CELL, CELL);
                cairo_fill(cr);
                if (ch == '.' || ch == '*') {
                    cairo_set_source_rgb(cr, 0.91, 0.27, 0.38);
                    cairo_arc(cr, rx + CELL / 2.0, ry + CELL / 2.0, 6, 0, 2 * G_PI);
                    cairo_fill(cr);
                }
                if (ch == '$' || ch == '*') {
                    if (ch == '*')
                        cairo_set_source_rgb(cr, 0.18, 0.80, 0.44);
                    else
                        cairo_set_source_rgb(cr, 0.95, 0.61, 0.07);
                    cairo_rectangle(cr, rx + 4, ry + 4, CELL - 8, CELL - 8);
                    cairo_fill(cr);
                }
            }
            if (x == g.px && y == g.py) {
                cairo_set_source_rgb(cr, 0.20, 0.60, 0.86);
                cairo_arc(cr, rx + CELL / 2.0, ry + CELL / 2.0, CELL * 0.32, 0, 2 * G_PI);
                cairo_fill(cr);
            }
        }
    }
    g_snprintf(status, sizeof(status), "moves=%d%s  WASD Z R Q", g.moves, g.won ? " WIN" : "");
    cairo_set_source_rgb(cr, 1, 1, 1);
    cairo_move_to(cr, 8, PAD + g.height * CELL + 16);
    cairo_show_text(cr, status);
    return FALSE;
}

static gboolean on_key(GtkWidget *widget, GdkEventKey *event, gpointer data)
{
    guint k = event->keyval;
    int dirty = 0;
    (void)data;
    if (k == GDK_KEY_w || k == GDK_KEY_W || k == GDK_KEY_Up)
        dirty = game_try_move(&g, 0, -1);
    else if (k == GDK_KEY_s || k == GDK_KEY_S || k == GDK_KEY_Down)
        dirty = game_try_move(&g, 0, 1);
    else if (k == GDK_KEY_a || k == GDK_KEY_A || k == GDK_KEY_Left)
        dirty = game_try_move(&g, -1, 0);
    else if (k == GDK_KEY_d || k == GDK_KEY_D || k == GDK_KEY_Right)
        dirty = game_try_move(&g, 1, 0);
    else if (k == GDK_KEY_z || k == GDK_KEY_Z)
        dirty = game_undo(&g);
    else if (k == GDK_KEY_r || k == GDK_KEY_R) {
        load();
        dirty = 1;
    } else if (k == GDK_KEY_q || k == GDK_KEY_Q || k == GDK_KEY_Escape) {
        gtk_main_quit();
        return TRUE;
    }
    if (dirty || k == GDK_KEY_w || k == GDK_KEY_W || k == GDK_KEY_Up ||
        k == GDK_KEY_s || k == GDK_KEY_S || k == GDK_KEY_Down ||
        k == GDK_KEY_a || k == GDK_KEY_A || k == GDK_KEY_Left ||
        k == GDK_KEY_d || k == GDK_KEY_D || k == GDK_KEY_Right ||
        k == GDK_KEY_z || k == GDK_KEY_Z || k == GDK_KEY_r || k == GDK_KEY_R)
        gtk_widget_queue_draw(widget);
    return TRUE;
}

int main(int argc, char **argv)
{
    GtkWidget *win, *da;

    gtk_init(&argc, &argv);
    load();

    win = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(win), "Sokoban GTK3 (teaching)");
    gtk_window_set_default_size(GTK_WINDOW(win),
                                PAD * 2 + g.width * CELL,
                                PAD * 2 + g.height * CELL + 28);
    g_signal_connect(win, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    da = gtk_drawing_area_new();
    gtk_widget_set_can_focus(da, TRUE);
    g_signal_connect(da, "draw", G_CALLBACK(on_draw), NULL);
    g_signal_connect(da, "key-press-event", G_CALLBACK(on_key), NULL);
    gtk_container_add(GTK_CONTAINER(win), da);

    gtk_widget_show_all(win);
    gtk_widget_grab_focus(da);
    gtk_main();
    return 0;
}
