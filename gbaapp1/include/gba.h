/* Minimal GBA hardware definitions (bare-metal) */
#ifndef SOKO_GBA_H
#define SOKO_GBA_H

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
typedef volatile u16 vu16;
typedef volatile u32 vu32;
typedef volatile u8 vu8;

#define REG_BASE 0x04000000
#define MEM_VRAM 0x06000000
#define MEM_EWRAM 0x02000000
#define MEM_IWRAM 0x03000000

#define REG_DISPCNT (*(vu16 *)(REG_BASE + 0x00))
#define REG_DISPSTAT (*(vu16 *)(REG_BASE + 0x04))
#define REG_VCOUNT (*(vu16 *)(REG_BASE + 0x06))
#define REG_KEYINPUT (*(vu16 *)(REG_BASE + 0x130))

#define REG_DMA3SAD (*(vu32 *)(REG_BASE + 0xD4))
#define REG_DMA3DAD (*(vu32 *)(REG_BASE + 0xD8))
#define REG_DMA3CNT (*(vu32 *)(REG_BASE + 0xDC))

#define DMA_DST_INC (0 << 21)
#define DMA_SRC_INC (0 << 23)
#define DMA_SRC_FIXED (2 << 23)
#define DMA_32 (1 << 26)
#define DMA_ENABLE (1u << 31)

#define REG_SOUND1CNT_L (*(vu16 *)(REG_BASE + 0x60))
#define REG_SOUND1CNT_H (*(vu16 *)(REG_BASE + 0x62))
#define REG_SOUND1CNT_X (*(vu16 *)(REG_BASE + 0x64))
#define REG_SOUNDCNT_L (*(vu16 *)(REG_BASE + 0x80))
#define REG_SOUNDCNT_H (*(vu16 *)(REG_BASE + 0x82))
#define REG_SOUNDCNT_X (*(vu16 *)(REG_BASE + 0x84))
#define REG_SOUNDBIAS (*(vu16 *)(REG_BASE + 0x88))

#define MODE_3 0x0003
#define BG2_ENABLE 0x0400

#define KEY_A 0x0001
#define KEY_B 0x0002
#define KEY_SELECT 0x0004
#define KEY_START 0x0008
#define KEY_RIGHT 0x0010
#define KEY_LEFT 0x0020
#define KEY_UP 0x0040
#define KEY_DOWN 0x0080
#define KEY_R 0x0100
#define KEY_L 0x0200
#define KEY_MASK 0x03FF

#define SCREEN_W 240
#define SCREEN_H 160

#define RGB15(r, g, b) ((u16)((r) | ((g) << 5) | ((b) << 10)))

static inline void vid_vsync(void)
{
	while (REG_VCOUNT >= 160)
		;
	while (REG_VCOUNT < 160)
		;
}

static inline u16 *vram(void) { return (u16 *)MEM_VRAM; }

static inline u16 key_poll(void) { return (u16)(~REG_KEYINPUT) & KEY_MASK; }

static inline void dma_copy32(void *dst, const void *src, u32 words)
{
	REG_DMA3SAD = (u32)src;
	REG_DMA3DAD = (u32)dst;
	REG_DMA3CNT = words | DMA_DST_INC | DMA_SRC_INC | DMA_32 | DMA_ENABLE;
}

static inline void dma_fill32(void *dst, u32 value, u32 words)
{
	volatile u32 v = value;
	REG_DMA3SAD = (u32)&v;
	REG_DMA3DAD = (u32)dst;
	REG_DMA3CNT = words | DMA_DST_INC | DMA_SRC_FIXED | DMA_32 | DMA_ENABLE;
}

#endif
