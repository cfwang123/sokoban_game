#include "game.h"

#pragma bss-name (push, "ZEROPAGE")
static unsigned char mus_ptr_lo;
static unsigned char mus_ptr_hi;
static unsigned char mus_wait;
static unsigned char mus_note;
#pragma bss-name (pop)

static const unsigned char note_lo[] = {
    0x00,
    0x56, 0x26, 0xF9, 0xCE, 0xA6, 0x80, 0x5C, 0x3A,
    0x1A, 0xFC, 0xE0, 0xC5, 0xAB, 0x93, 0x7C
};
static const unsigned char note_hi[] = {
    0x00,
    0x03, 0x03, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
    0x02, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01
};

/* soft puzzle BGM: duration, note ... $FF loop */
static const unsigned char puzzle_music[] = {
    16,5, 16,8, 16,10, 16,8,
    16,5, 16,3, 16,5, 24,0,
    16,8, 16,10, 16,12, 16,10,
    16,8, 16,5, 16,3, 24,0,
    0xFF
};

static void mus_set_ptr(const unsigned char *p)
{
    mus_ptr_lo = (unsigned char)((unsigned)p & 0xFF);
    mus_ptr_hi = (unsigned char)(((unsigned)p >> 8) & 0xFF);
}

static unsigned char mus_read(unsigned char off)
{
    unsigned char *p = (unsigned char *)(mus_ptr_lo | (mus_ptr_hi << 8));
    return p[off];
}

void music_init(void)
{
    mus_set_ptr(puzzle_music);
    mus_wait = 1;
    SND_CHN = 0x0F;
    SQ1_VOL = 0x90;
    SQ1_SWEEP = 0;
    SQ2_VOL = 0x90;
    SQ2_SWEEP = 0;
    TRI_LINEAR = 0x81;
}

void music_update(void)
{
    unsigned char n, idx;

    if (sfx_timer)
        return; /* let SFX use pulse */

    if (--mus_wait != 0)
        return;

    n = mus_read(0);
    if (n == 0xFF) {
        mus_set_ptr(puzzle_music);
        n = mus_read(0);
    }
    mus_wait = n;
    mus_note = mus_read(1);

    {
        unsigned p = mus_ptr_lo | (mus_ptr_hi << 8);
        p += 2;
        mus_ptr_lo = (unsigned char)(p & 0xFF);
        mus_ptr_hi = (unsigned char)((p >> 8) & 0xFF);
    }

    if (mus_note) {
        idx = mus_note;
        SQ1_LO = note_lo[idx];
        SQ1_HI = (unsigned char)(note_hi[idx] | 0x08);
        SQ1_VOL = 0x9A;
    } else {
        SQ1_VOL = 0x90;
    }
}

void sfx_move(void)
{
    SQ2_VOL = 0x88;
    SQ2_LO = 0xC0;
    SQ2_HI = 0x0A;
    sfx_timer = 3;
}

void sfx_push(void)
{
    SQ2_VOL = 0x9F;
    SQ2_LO = 0x60;
    SQ2_HI = 0x09;
    sfx_timer = 6;
}

void sfx_block(void)
{
    NOISE_VOL = 0x12;
    NOISE_LO = 0x0D;
    NOISE_HI = 0x18;
    sfx_timer = 4;
}

void sfx_undo(void)
{
    SQ2_VOL = 0x9A;
    SQ2_LO = 0x20;
    SQ2_HI = 0x0A;
    sfx_timer = 5;
}

void sfx_win(void)
{
    SQ1_VOL = 0x9F;
    SQ1_LO = 0x20;
    SQ1_HI = 0x09;
    sfx_timer = 40;
}

void sfx_reset(void)
{
    SQ2_VOL = 0x9A;
    SQ2_LO = 0x00;
    SQ2_HI = 0x0B;
    sfx_timer = 8;
}
