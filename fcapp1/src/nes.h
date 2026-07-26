/* NES / Famicom MMIO and game constants */
#ifndef NES_H
#define NES_H

/* ---- PPU ---- */
#define PPUCTRL   (*(volatile unsigned char *)0x2000)
#define PPUMASK   (*(volatile unsigned char *)0x2001)
#define PPUSTATUS (*(volatile unsigned char *)0x2002)
#define OAMADDR   (*(volatile unsigned char *)0x2003)
#define OAMDATA   (*(volatile unsigned char *)0x2004)
#define PPUSCROLL (*(volatile unsigned char *)0x2005)
#define PPUADDR   (*(volatile unsigned char *)0x2006)
#define PPUDATA   (*(volatile unsigned char *)0x2007)
#define OAMDMA    (*(volatile unsigned char *)0x4014)

/* ---- APU / Input ---- */
#define SQ1_VOL    (*(volatile unsigned char *)0x4000)
#define SQ1_SWEEP  (*(volatile unsigned char *)0x4001)
#define SQ1_LO     (*(volatile unsigned char *)0x4002)
#define SQ1_HI     (*(volatile unsigned char *)0x4003)
#define SQ2_VOL    (*(volatile unsigned char *)0x4004)
#define SQ2_SWEEP  (*(volatile unsigned char *)0x4005)
#define SQ2_LO     (*(volatile unsigned char *)0x4006)
#define SQ2_HI     (*(volatile unsigned char *)0x4007)
#define TRI_LINEAR (*(volatile unsigned char *)0x4008)
#define TRI_LO     (*(volatile unsigned char *)0x400A)
#define TRI_HI     (*(volatile unsigned char *)0x400B)
#define NOISE_VOL  (*(volatile unsigned char *)0x400C)
#define NOISE_LO   (*(volatile unsigned char *)0x400E)
#define NOISE_HI   (*(volatile unsigned char *)0x400F)
#define DMC_FREQ   (*(volatile unsigned char *)0x4010)
#define SND_CHN    (*(volatile unsigned char *)0x4015)
#define JOY1       (*(volatile unsigned char *)0x4016)
#define JOY2       (*(volatile unsigned char *)0x4017)

/* Game states */
#define ST_TITLE  0
#define ST_PLAY   1
#define ST_WIN    2
#define ST_MENU   3
#define ST_ANSWER 4

/* Pause menu items */
#define MENU_RESET  0
#define MENU_NEXT   1
#define MENU_ANS    2
#define MENU_COUNT  3

/* Solution step encoding (see gen_levels.py) */
#define SOL_U 0
#define SOL_D 1
#define SOL_L 2
#define SOL_R 3

/* Controller bits */
#define PAD_R      0x01
#define PAD_L      0x02
#define PAD_D      0x04
#define PAD_U      0x08
#define PAD_START  0x10
#define PAD_SELECT 0x20
#define PAD_B      0x40
#define PAD_A      0x80

/* Map limits (8x8 cell tiles; max level ~20x17 fits 32x28 play area) */
#define MAP_MAX_W  20
#define MAP_MAX_H  18
#define MAP_MAX    (MAP_MAX_W * MAP_MAX_H)

/* Cell flags (bitmask in map_cells) */
#define C_WALL  0x01
#define C_GOAL  0x02
#define C_BOX   0x04

/* Undo stack depth */
#define HIST_MAX  48

/* BG tile indices (pattern table 0) */
#define TILE_FLOOR  1
#define TILE_WALL   2
#define TILE_GOAL   3
#define TILE_BOX    4
#define TILE_BOXG   5
#define TILE_HUD    6
#define TILE_PANEL  7
#define TILE_EDGE   8

/* Sprite tile indices (pattern table 1) */
#define SPR_PLAYER  1
#define SPR_DIGIT0  0x10   /* 0-9 at 0x10..0x19 */
#define SPR_SPACE   0x20
#define SPR_A       0x21   /* A-Z at 0x21..0x3A */
#define SPR_GT      0x3E   /* > cursor */

#endif
