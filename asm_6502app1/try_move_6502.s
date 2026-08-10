; try_move_6502.s — 6502 教学骨架（ca65 语法风格）
; 与仓库 fcapp1（NES）同源生态
; 完整玩法见 ../asm_common/game.c 与 ../fcapp1

        .export sk_try_move_6502_demo
sk_try_move_6502_demo:
        lda #0
        rts

; 教学: A/X/Y、零页、绝对/间接寻址、无乘除指令
; 推箱状态宜放零页: player_x, player_y, ...
