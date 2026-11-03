; main.asm - bank 7: start, the frame, and what is done
; in it besides the kernels:
; - the buttons: RESET starts again;
; - setting a room up: its playfield comes from bank 3
;   into the Superchip RAM;
; - what the kernels need: Sir Roderick, the colours of
;   the room, the HUD.

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
        jsr     digits          ; the score's digits
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
        sta     score
        sta     score+1
        sta     score+2
        lda     #ENERGY_FULL
        sta     energy
        lda     #$FF
        sta     shown           ; the room is set up again
        jmp     digits          ; (score 0)

; ---------------------------------------------------------
; setup_room: when the screen changes, the playfield of
; the room goes into the Superchip RAM (bank 3)
; - with its door open;
; - the HUD gets the name of its level; the plug of the
;   room is chosen;

setup_room:
        lda     screen
        cmp     shown
        beq     su_done
        sta     shown
        jsr     TO_COPY         ; bank 3: room_copy
su_copied:                      ; the tests time the copy
        lda     room            ; the name of the level
        lsr
        lsr
        tax
        jsr     name
        ldx     room
su_plug:
        lda     PLUG,x          ; the ball on or off
        sta     plug
su_done:
        rts

; name: the six pointers of the name in the HUD, X = 0-3
; the level - 1, 4 GAME OVER: one a column of 8 bytes, the
; sixth 40 bytes after the first (room_state adds 8 for the
; key); the 56 bytes are in one page: one high byte
name:   lda     TX_HI,x
        sta     txp+1
        sta     txp+3
        sta     txp+5
        sta     txp+7
        sta     txp+9
        sta     txp+11
        lda     TX_LO,x
        sta     txp
        clc                     ; (no carry: one page)
        adc     #8
        sta     txp+2
        adc     #8
        sta     txp+4
        adc     #8
        sta     txp+6
        adc     #8
        sta     txp+8
        adc     #8
        sta     txp+10
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
; colours of the room, the torches, the energy bar; the
; blade; the positions of the six digits of the HUD, of
; the blade, of the ball

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
        ; colours of the room: its scheme gives COLUBK (the
        ; water changes it) and COLUPF
        ldx     room
        ldy     SCHEME,x
        lda     frames
        and     #8
        beq     pr_col0
        lda     CB1_LO,y
        sta     cbk
        lda     CB1_HI,y
        bne     pr_col          ; (never 0)
pr_col0:
        lda     CB0_LO,y
        sta     cbk
        lda     CB0_HI,y
pr_col: sta     cbk+1
        lda     CP_LO,y
        sta     cpf
        lda     CP_HI,y
        sta     cpf+1
        ; torches: course 0 changes every four frames
        lda     RF_HI,x
        beq     pr_digits
        sta     tmp+1
        lda     RF_LO,x
        sta     tmp
        ldy     #3              ; bit 2 of frames clear: the
        lda     frames          ; flame stays in its niche
        and     #4
        beq     pr_t0
        ldy     #0              ; bit 2 set: it rises
pr_t0:
        lda     (tmp),y
        sta     SCW+SC_PF0+19
        iny
        lda     (tmp),y
        sta     SCW+SC_PF1+19
        iny
        lda     (tmp),y
        sta     SCW+SC_PF2+19
pr_digits:
        ; (the digits are pointed to in the overscan,
        ; after the points: digits)
        ; energy bar
        ldx     energy
        lda     BAR_PF1,x
        sta     bar1
        lda     BAR_PF2,x
        sta     bar2
        jsr     blade           ; knight.asm
        ; positions: the six digits with players 0 and 1, 8
        ; pixels apart, three copies each, both delayed; the
        ; blade with missile 0 (RESMP0 first: while it is 2
        ; the missile stays on player 0); the ball where the
        ; room has its plug (in any room: it shows only when
        ; ENABL is on)
        lda     swres
        sta     RESMP0
        lda     #SCORE_X
        ldx     #0
        jsr     place
        lda     #SCORE_X+8
        ldx     #1
        jsr     place
        lda     swx
        ldx     #2
        jsr     place
        ldx     room
        lda     BALL_X,x
        ldx     #4
        jsr     place
pr_hmove:
        sta     WSYNC
        sta     HMOVE           ;  2
        lda     #3
        sta     NUSIZ0
        sta     NUSIZ1
        lda     #1
        sta     VDELP0
        sta     VDELP1
        lda     #$31            ; reflected playfield, the
        sta     CTRLPF          ; ball 8 pixels wide
        lda     #0
        sta     REFP0
        sta     REFP1
        sta     HMCLR           ; 34: 32 cycles after HMOVE
        rts

; digits: the six pointers of the score in the HUD, digit d
; at DIGITS + 8 d (in the overscan of a game, after the
; things that add points, and in new_game; not in the
; VBLANK, which is short when a room changes)
digits: ldx     #0
        ldy     #0
di_one: lda     score,x
        lsr
        lsr
        lsr
        lsr
        jsr     dig_ptr
        lda     score,x
        and     #$0F
        jsr     dig_ptr
        inx
        cpx     #3
        bne     di_one
        rts

; dig_ptr: A = digit; pointer Y in dig (Y += 2)
dig_ptr:
        asl
        asl
        asl
        clc
        adc     #<DIGITS
        sta     dig,y
        lda     #>DIGITS
        adc     #0
        sta     dig+1,y
        iny
        iny
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
