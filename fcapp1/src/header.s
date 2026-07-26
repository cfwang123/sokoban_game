; iNES header — NROM-256 mapper 0, 32KB PRG, 8KB CHR, horizontal mirroring
.segment "HEADER"
    .byte "NES", $1A
    .byte $02          ; 2 x 16KB PRG
    .byte $01          ; 1 x 8KB CHR
    .byte $00          ; mapper 0, horizontal
    .byte $00
    .res 8, $00
