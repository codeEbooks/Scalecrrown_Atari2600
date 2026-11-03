; main.asm - bank 7: start, the frame, and what is done
; in it besides the kernels:
; - setting a room up: its playfield comes from bank 3
;   into the Superchip RAM;
; - what the kernels need: Sir Roderick, the colours of
;   the room.

start:
        sei
        cld
        ldx     #0
        txa
clear:  sta     0,x             ; TIA and RAM
        dex
        bne     clear
        dex
        txs                     ; stack at $FF
        lda     #$FF
        sta     shown           ; no room set up yet
        jsr     new_game        ; the game at once
        jmp     main

kernel_done:                    ; back from a kernel (the
                                ; overscan timer is running)
over_wait:
        lda     INTIM
        bne     over_wait

main:   lda     #2              ; VSYNC: three lines,
        sta     WSYNC           ; 228 cycles
        sta     VSYNC
        sta     VBLANK
        sta     WSYNC
        sta     WSYNC
        lsr
        sta     WSYNC
        sta     VSYNC
        lda     #VBLANK_TIM
        sta     TIM64T
        inc     frames
frame_ready:                    ; the tests stop here
fr_room:
        jsr     setup_room
        jsr     prep_room
vb_end:                         ; the tests read INTIM here
        lda     INTIM
        bne     vb_end
        sta     WSYNC
        jmp     hud             ; HUD (hud.asm), then room

; ---------------------------------------------------------
; new_game: Sir Roderick at the start, in the first room

new_game:
        lda     #START_ROOM
        sta     room
        tax
        inx
        stx     screen
        lda     #START_X
        sta     kx
        lda     #START_TOP
        sta     ky
        lda     #0
        sta     kdir            ; facing right
        sta     kpose
        lda     #$FF
        sta     shown           ; the room is set up again
        rts

; ---------------------------------------------------------
; setup_room: when the screen changes, the playfield of
; the room goes into the Superchip RAM (bank 3)

setup_room:
        lda     screen
        cmp     shown
        beq     su_done
        sta     shown
        jsr     TO_COPY         ; bank 3: room_copy
su_copied:                      ; the tests time the copy
su_done:
        rts

; ---------------------------------------------------------
; prep_room: the pointers of Sir Roderick and of the
; colours of the room

prep_room:
        ; Sir Roderick: pose kpose, top line ky
        ldy     kpose
        lda     KG_LO,y
        clc
        adc     ky
        sta     kgfx
        lda     KG_HI,y
        adc     #0
        sta     kgfx+1
pr_kc:  lda     KC_LO,y
        clc
        adc     ky
        sta     kcol
        lda     KC_HI,y
        adc     #0
        sta     kcol+1
        ; colours of the room: its scheme gives COLUBK and
        ; COLUPF
        ldx     room
        ldy     SCHEME,x
        lda     CB0_LO,y
        sta     cbk
        lda     CB0_HI,y
pr_col: sta     cbk+1
        lda     CP_LO,y
        sta     cpf
        lda     CP_HI,y
        sta     cpf+1
pr_hmove:
        lda     #$31            ; reflected playfield, the
        sta     CTRLPF          ; ball 8 pixels wide
        rts
