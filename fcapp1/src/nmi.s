.include "defs.inc"
.importzp _nmi_ready, _frame_cnt, _sfx_timer
.import _music_update
.export nmi, irq

.segment "CODE"

nmi:
    pha
    txa
    pha
    tya
    pha

    lda _nmi_ready
    beq @skip_dma
    ; OAM DMA from $0200
    lda #0
    sta OAMADDR
    lda #$02
    sta OAMDMA

    ; scroll
    lda #0
    sta PPUSCROLL
    lda #0
    sta PPUSCROLL

    ; NMI on, BG $0000 (bit4=0), SPR $1000 (bit3=1) = %10001000
    lda #%10001000
    sta PPUCTRL
    lda #%00011110
    sta PPUMASK

    lda #0
    sta _nmi_ready
@skip_dma:
    inc _frame_cnt

    jsr _music_update
    lda _sfx_timer
    beq @nosfx
    dec _sfx_timer
@nosfx:

    pla
    tay
    pla
    tax
    pla
    rti

irq:
    rti
