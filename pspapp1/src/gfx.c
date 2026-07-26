#include "gfx.h"

#include <pspgu.h>
#include <pspdisplay.h>
#include <pspge.h>

static char list[0x40000] __attribute__((aligned(64)));
static void *fbp0;
static void *fbp1;

typedef struct {
    short x, y, z;
} Vertex2D;

void gfx_init(void)
{
    fbp0 = guGetStaticVramBuffer(BUF_W, BUF_H, GU_PSM_8888);
    fbp1 = guGetStaticVramBuffer(BUF_W, BUF_H, GU_PSM_8888);

    sceGuInit();
    sceGuStart(GU_DIRECT, list);

    sceGuDrawBuffer(GU_PSM_8888, fbp0, BUF_W);
    sceGuDispBuffer(SCREEN_W, SCREEN_H, fbp1, BUF_W);
    sceGuDepthBuffer(fbp0, 0);
    sceGuDisable(GU_DEPTH_TEST);

    sceGuOffset(2048 - (SCREEN_W / 2), 2048 - (SCREEN_H / 2));
    sceGuViewport(2048, 2048, SCREEN_W, SCREEN_H);
    sceGuEnable(GU_SCISSOR_TEST);
    sceGuScissor(0, 0, SCREEN_W, SCREEN_H);

    sceGuEnable(GU_BLEND);
    sceGuBlendFunc(GU_ADD, GU_SRC_ALPHA, GU_ONE_MINUS_SRC_ALPHA, 0, 0);

    sceGuFinish();
    sceGuSync(0, 0);
    sceDisplayWaitVblankStart();
    sceGuDisplay(GU_TRUE);
}

void gfx_shutdown(void)
{
    sceGuDisplay(GU_FALSE);
    sceGuTerm();
}

void gfx_begin(uint32_t clear_color)
{
    sceGuStart(GU_DIRECT, list);
    sceGuClearColor(clear_color);
    sceGuClear(GU_COLOR_BUFFER_BIT);
    sceGuDisable(GU_TEXTURE_2D);
}

void gfx_end(void)
{
    sceGuFinish();
    sceGuSync(0, 0);
    sceDisplayWaitVblankStart();
    sceGuSwapBuffers();
}

void gfx_rect(float x, float y, float w, float h, uint32_t color)
{
    Vertex2D *v = (Vertex2D *)sceGuGetMemory(2 * sizeof(Vertex2D));
    v[0].x = (short)x;
    v[0].y = (short)y;
    v[0].z = 0;
    v[1].x = (short)(x + w);
    v[1].y = (short)(y + h);
    v[1].z = 0;

    sceGuColor(color);
    sceGuDrawArray(GU_SPRITES, GU_VERTEX_16BIT | GU_TRANSFORM_2D, 2, 0, v);
}

void gfx_rect_border(float x, float y, float w, float h, float t, uint32_t color)
{
    gfx_rect(x, y, w, t, color);
    gfx_rect(x, y + h - t, w, t, color);
    gfx_rect(x, y, t, h, color);
    gfx_rect(x + w - t, y, t, h, color);
}
