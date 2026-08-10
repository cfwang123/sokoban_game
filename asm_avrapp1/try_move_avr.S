; try_move_avr.S — AVR 教学骨架（ATmega 风格）
; 8 位寄存器 r0–r31；参数多通过寄存器对传递
; 完整玩法: ../asm_common/game.c（主机侧）
; 本文件演示推箱判定伪指令序列

        .global sk_try_move_avr_demo
sk_try_move_avr_demo:
        clr     r24           ; 返回 0 (16-bit 在 r25:r24)
        clr     r25
        ret

; 教学: X/Y/Z 指针寄存器、SREG 状态、Harvard 架构
