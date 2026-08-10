; try_move_z80.asm — Z80 教学骨架
; 8 位经典机（Spectrum、Game Boy 前身相关生态）
; 完整玩法算法见 ../asm_common/game.c
;
; HL = game 指针（教学假设）
; DE = dx,dy 打包等 — 具体由宿主约定

        PUBLIC sk_try_move_z80_demo
sk_try_move_z80_demo:
        ld      a, 0
        ret

; 教学: AF/BC/DE/HL、影子寄存器、IX/IY
