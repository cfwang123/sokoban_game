/**
 * @file wqx_hal_stub.c
 * @brief 文曲星 HAL 教学桩实现（非真机固件）
 *
 * 作用：
 *  - 让工程在「没有厂商 SDK」时仍能通过结构审查 / 静态阅读；
 *  - 说明每个 API 在真机上大致应对接什么。
 *
 * 真机移植步骤（示意）：
 *  1. 新建 wqx_hal_device.c，实现 wqx_api.h 中全部函数；
 *  2. Makefile 用 device 源替换本 stub；
 *  3. 按机型改 WQX_LCD_W/H 与键值映射。
 *
 * 可选：在 PC 上另写 wqx_hal_sdl.c 用窗口模拟灰阶屏（本仓库不要求）。
 */

#include "wqx/wqx_api.h"

#include <stdio.h>
#include <string.h>

static unsigned s_prev_keys;
static unsigned char s_nv_level = 0;
static int s_frame;

/* 简易 6x8 字模仅数字与大写（演示用，极简） */
static const unsigned char FONT6X8_QMARK[8] = {
    0x3C, 0x42, 0x02, 0x0C, 0x10, 0x00, 0x10, 0x00
};

int wqx_init(void) {
    s_prev_keys = 0;
    s_frame = 0;
    /* 真机：打开显示驱动、键中断、背光 */
    printf("[wqx-stub] init LCD %dx%d\n", WQX_LCD_W, WQX_LCD_H);
    return 0;
}

void wqx_shutdown(void) {
    printf("[wqx-stub] shutdown\n");
}

void wqx_clear(wqx_gray_t g) {
    (void)g;
    /* 真机：清帧缓冲 */
}

void wqx_flush(void) {
    s_frame++;
    /* 真机：DMA/SPI 推屏；stub 每 30 帧打一行日志避免刷屏 */
    if ((s_frame % 30) == 0) {
        printf("[wqx-stub] flush frame %d\n", s_frame);
    }
}

void wqx_fill_rect(int x, int y, int w, int h, wqx_gray_t g) {
    (void)x;
    (void)y;
    (void)w;
    (void)h;
    (void)g;
}

void wqx_draw_rect(int x, int y, int w, int h, wqx_gray_t g) {
    (void)x;
    (void)y;
    (void)w;
    (void)h;
    (void)g;
}

void wqx_fill_circle(int cx, int cy, int r, wqx_gray_t g) {
    (void)cx;
    (void)cy;
    (void)r;
    (void)g;
}

void wqx_draw_text(int x, int y, const char *ascii, wqx_gray_t g) {
    (void)x;
    (void)y;
    (void)g;
    (void)FONT6X8_QMARK;
    /* 真机：查字模写点阵；stub 可输出调试 */
    if (ascii && (s_frame % 60) == 1) {
        printf("[wqx-stub] text: %s\n", ascii);
    }
}

void wqx_delay_ms(unsigned ms) {
    (void)ms;
    /* 真机：系统 tick 睡眠；stub 空转即可（演示不跑实时循环） */
}

unsigned wqx_key_poll(void) {
    /* 真机：读 GPIO / 键矩阵；stub 无输入 */
    return 0;
}

unsigned wqx_key_pressed(void) {
    unsigned now = wqx_key_poll();
    unsigned edge = now & ~s_prev_keys;
    s_prev_keys = now;
    return edge;
}

int wqx_nv_load_u8(unsigned id, unsigned char *out) {
    if (!out) {
        return -1;
    }
    if (id == WQX_NV_LAST_LEVEL) {
        *out = s_nv_level;
        return 0;
    }
    return -1;
}

int wqx_nv_save_u8(unsigned id, unsigned char value) {
    if (id == WQX_NV_LAST_LEVEL) {
        s_nv_level = value;
        return 0;
    }
    return -1;
}
