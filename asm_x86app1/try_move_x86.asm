; try_move_x86.asm — full sk_try_move (NASM, IA-32 cdecl)
; int sk_try_move(SkGame *g, int dx, int dy)
;   [ebp+8]=g [ebp+12]=dx [ebp+16]=dy → eax
; Locals: [ebp-4]=nx [ebp-8]=ny [ebp-12]=bx [ebp-16]=by
; Layout: ../asm_common/game.h  map stride 32
; nasm -f elf32 try_move_x86.asm   OR  nasm -f win32 try_move_x86.asm

        global  sk_try_move
        section .text

sk_try_move:
        push    ebp
        mov     ebp, esp
        sub     esp, 16
        push    ebx
        push    esi
        push    edi

        mov     esi, [ebp+8]            ; g
        cmp     dword [esi+1044], 0
        jne     .fail

        mov     eax, [esi+1032]
        add     eax, [ebp+12]
        mov     [ebp-4], eax            ; nx
        mov     eax, [esi+1036]
        add     eax, [ebp+16]
        mov     [ebp-8], eax            ; ny

        mov     eax, [ebp-4]
        mov     edx, [ebp-8]
        call    .at
        cmp     al, '#'
        je      .fail
        cmp     al, '$'
        je      .push
        cmp     al, '*'
        je      .push

        ; walk
        cmp     dword [esi+1048], 256
        jge     .fail
        mov     eax, [esi+1048]
        imul    eax, 28
        lea     edi, [esi+1052+eax]
        mov     eax, [esi+1032]
        mov     [edi], eax
        mov     eax, [esi+1036]
        mov     [edi+4], eax
        mov     dword [edi+24], 0
        inc     dword [esi+1048]
        mov     eax, [ebp-4]
        mov     [esi+1032], eax
        mov     eax, [ebp-8]
        mov     [esi+1036], eax
        mov     eax, 1
        jmp     .done

.push:
        mov     eax, [ebp-4]
        add     eax, [ebp+12]
        mov     [ebp-12], eax           ; bx
        mov     eax, [ebp-8]
        add     eax, [ebp+16]
        mov     [ebp-16], eax           ; by

        mov     eax, [ebp-12]
        mov     edx, [ebp-16]
        call    .at
        cmp     al, '#'
        je      .fail
        cmp     al, '$'
        je      .fail
        cmp     al, '*'
        je      .fail
        cmp     dword [esi+1048], 256
        jge     .fail

        mov     eax, [esi+1048]
        imul    eax, 28
        lea     edi, [esi+1052+eax]
        mov     eax, [esi+1032]
        mov     [edi], eax
        mov     eax, [esi+1036]
        mov     [edi+4], eax
        mov     eax, [ebp-4]
        mov     [edi+8], eax
        mov     eax, [ebp-8]
        mov     [edi+12], eax
        mov     eax, [ebp-12]
        mov     [edi+16], eax
        mov     eax, [ebp-16]
        mov     [edi+20], eax
        mov     dword [edi+24], 1
        inc     dword [esi+1048]

        ; clear from
        mov     eax, [ebp-4]
        mov     edx, [ebp-8]
        call    .at
        cmp     al, '*'
        mov     al, '.'
        je      .c1
        mov     al, ' '
.c1:    mov     edx, [ebp-8]
        mov     ecx, [ebp-4]
        call    .set_edx_ecx_al

        ; place box
        mov     eax, [ebp-12]
        mov     edx, [ebp-16]
        call    .at
        cmp     al, '.'
        mov     al, '*'
        je      .c2
        mov     al, '$'
.c2:    mov     edx, [ebp-16]
        mov     ecx, [ebp-12]
        call    .set_edx_ecx_al

        mov     eax, [ebp-4]
        mov     [esi+1032], eax
        mov     eax, [ebp-8]
        mov     [esi+1036], eax
        inc     dword [esi+1040]
        call    .check_win
        mov     eax, 1
        jmp     .done

.fail:  xor     eax, eax
.done:  pop     edi
        pop     esi
        pop     ebx
        mov     esp, ebp
        pop     ebp
        ret

; at: eax=x edx=y  esi=g → al
.at:    cmp     eax, 0
        jl      .wall
        cmp     edx, 0
        jl      .wall
        cmp     eax, [esi+1024]
        jge     .wall
        cmp     edx, [esi+1028]
        jge     .wall
        shl     edx, 5
        add     edx, eax
        mov     al, [esi+edx]
        ret
.wall:  mov     al, '#'
        ret

; set: ecx=x edx=y al=c  esi=g
.set_edx_ecx_al:
        mov     ebx, edx
        shl     ebx, 5
        add     ebx, ecx
        mov     [esi+ebx], al
        ret

.check_win:
        mov     dword [esi+1044], 1
        xor     edx, edx
.cy:    cmp     edx, [esi+1028]
        jge     .cwd
        xor     eax, eax
.cx:    cmp     eax, [esi+1024]
        jge     .cxd
        mov     ecx, edx
        shl     ecx, 5
        add     ecx, eax
        cmp     byte [esi+ecx], '$'
        jne     .n1
        mov     dword [esi+1044], 0
.n1:    inc     eax
        jmp     .cx
.cxd:   inc     edx
        jmp     .cy
.cwd:   ret
