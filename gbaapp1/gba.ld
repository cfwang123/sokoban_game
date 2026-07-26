OUTPUT_FORMAT("elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(_start)

MEMORY
{
    rom (rx)  : ORIGIN = 0x08000000, LENGTH = 0x02000000
    iwram (rwx) : ORIGIN = 0x03000000, LENGTH = 0x00008000
    ewram (rwx) : ORIGIN = 0x02000000, LENGTH = 0x00040000
}

__sp_irq = 0x03007FA0;
__sp_usr = 0x03007F00;

SECTIONS
{
    .text :
    {
        KEEP(*(.text.boot))
        *(.text*)
        *(.rodata*)
        . = ALIGN(4);
    } > rom

    .data :
    {
        __data_start = .;
        *(.data*)
        . = ALIGN(4);
        __data_end = .;
    } > ewram AT > rom

    __data_lma = LOADADDR(.data);

    .bss (NOLOAD) :
    {
        __bss_start = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        __bss_end = .;
    } > ewram

    .ewram (NOLOAD) :
    {
        *(.ewram*)
        . = ALIGN(4);
    } > ewram
}
