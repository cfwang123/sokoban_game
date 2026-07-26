.include "defs.inc"
.import nmi, irq
.import _main
.importzp c_sp
.export reset
.export __STARTUP__ : absolute = 1

.segment "CODE"

reset:
    sei
    cld
    ldx #$40
    stx JOY2            ; disable APU frame IRQ
    ldx #$FF
    txs
    inx                 ; X=0
    stx PPUCTRL
    stx PPUMASK
    stx DMC_FREQ

@v1:
    bit PPUSTATUS
    bpl @v1
@v2:
    bit PPUSTATUS
    bpl @v2

    ; clear RAM $0000-$07FF
    lda #0
    tax
@clr:
    sta $0000,x
    sta $0100,x
    sta $0200,x
    sta $0300,x
    sta $0400,x
    sta $0500,x
    sta $0600,x
    sta $0700,x
    inx
    bne @clr

    lda #$FF
    ldx #0
@o:
    sta $0200,x
    inx
    bne @o

@v3:
    bit PPUSTATUS
    bpl @v3

    ; palette
    lda #$3F
    sta PPUADDR
    lda #$00
    sta PPUADDR
    ldx #0
@pal:
    lda palette,x
    sta PPUDATA
    inx
    cpx #32
    bne @pal

    ; C software stack: $0700-$07FF (grows down)
    lda #$FF
    sta c_sp
    lda #$07
    sta c_sp+1

    jmp _main

palette:
    ; One map palette for all BG (no attr bleed):
    ; 0 black | 1 gray WALL | 2 blue FLOOR | 3 gold BOX / accents
    .byte $0F,$00,$21,$28
    .byte $0F,$00,$21,$28
    .byte $0F,$00,$21,$28
    .byte $0F,$00,$21,$28
    ; SPR0 player — orange/red (distinct from blue floor $21 and gold box $28)
    ;   0 black | 1 dark red outline | 2 mid orange | 3 bright orange
    .byte $0F,$06,$16,$27
    ; SPR1 spare (green accents)
    .byte $0F,$0A,$1A,$2A
    ; SPR2 HUD text white
    .byte $0F,$00,$10,$30
    ; SPR3 menu yellow
    .byte $0F,$28,$38,$30

.segment "VECTORS"
    .word nmi
    .word reset
    .word irq
