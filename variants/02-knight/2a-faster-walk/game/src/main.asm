; main.asm - bank 7: start, the frame, and what is done
; in it besides the kernels:
; - the buttons: RESET starts again;
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
        jsr     buttons
fr_game:
        lda     pressed
        lsr                     ; bit 0: RESET
        bcc     fr_play
        jsr     new_game        ; start again
        jmp     fr_room
fr_play:
fr_knight:
        jsr     knight          ; Sir Roderick (knight.asm)
fr_room:
        jsr     setup_room
        jsr     room_state
        jsr     prep_room
vb_end:                         ; the tests read INTIM here
        lda     INTIM
        bne     vb_end
        sta     WSYNC
        jmp     hud             ; HUD (hud.asm), then room

; ---------------------------------------------------------
; buttons: pressed = down in this frame and up in the one
; before; fire $80, SELECT $02, RESET $01 (all are 0 when
; down)

buttons:
        lda     INPT4           ; bit 7: the fire button
        eor     #$FF
        and     #$80
        sta     tmp
        lda     SWCHB           ; bit 0 RESET, bit 1 SELECT
        eor     #$FF
        and     #$03
        ora     tmp
        tax                     ; down now
        eor     held            ; changed
        stx     held
        and     held            ; changed and down now
        sta     pressed
        rts

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
        sta     kdist
        sta     hacc
        sta     vacc
        sta     thrust
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
; room_state: in every frame of a game, what follows from
; the room: its collision map

room_state:
        ldx     room
        lda     CM_LO,x         ; open (or no door)
        ldy     CM_HI,x
rs_map: sta     cmap
        sty     cmap+1
        rts

; ---------------------------------------------------------
; prep_room: the pointers of Sir Roderick and of the
; colours of the room; the blade and its position

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
        jsr     blade           ; knight.asm
        ; the position of the blade, missile 0 (RESMP0
        ; first: while it is 2 the missile stays on player
        ; 0; the HMOVE of HUD line 28 moves it with Sir
        ; Roderick)
        lda     swres
        sta     RESMP0
        lda     swx
        ldx     #2
        jsr     place
pr_hmove:
        lda     #$31            ; reflected playfield, the
        sta     CTRLPF          ; ball 8 pixels wide
        rts

; place: object X (0 player 0, 1 player 1, 2 missile 0, 3
; missile 1, 4 the ball) at column A: the first pixel of a
; player is A + 3, of a missile or the ball A + 2. Takes one
; line: the WSYNC, then 15 pixels per 5 cycles.
; (its loop in one page: a branch that crosses one takes a
; cycle more, and the column would be wrong; the padding
; comes after an rts)
        IF (* & $FF00) != ((*+8) & $FF00)
        ALIGN   256
        ENDIF
place:
        sta     WSYNC
        sec
pl_div: sbc     #15
        bcs     pl_div          ; (pl_div)
        eor     #7
        asl
        asl
        asl
        asl
        sta     HMP0,x
        sta     RESP0,x
        rts
