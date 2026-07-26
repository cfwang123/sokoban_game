/* GBA bare-metal startup */
    .section .text.boot, "ax", %progbits
    .global _start
    .cpu arm7tdmi
    .arm

_start:
    b       reset_handler
    .space  0xE0

reset_handler:
    mov     r0, #0x12
    msr     cpsr_c, r0
    ldr     sp, =__sp_irq

    mov     r0, #0x1F
    msr     cpsr_c, r0
    ldr     sp, =__sp_usr

    ldr     r0, =__data_lma
    ldr     r1, =__data_start
    ldr     r2, =__data_end
1:
    cmp     r1, r2
    bge     2f
    ldr     r3, [r0], #4
    str     r3, [r1], #4
    b       1b
2:
    ldr     r0, =__bss_start
    ldr     r1, =__bss_end
    mov     r2, #0
3:
    cmp     r0, r1
    bge     4f
    str     r2, [r0], #4
    b       3b
4:
    ldr     r0, =main
    bx      r0

hang:
    b       hang
