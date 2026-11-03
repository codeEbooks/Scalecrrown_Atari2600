; ends_kernel.asm - bank 6: the end screens
;
; GAME OVER and VICTORY. Entered as the title kernel is
; (main.asm: jmp TO_ENDS right after the WSYNC that ends the
; VBLANK), and laid out like the title: 192 lines (PAL: 18
; black lines above and below), drawn with the two macros of
; title_kernel.asm on the tables of this bank (bank6.asm):
;   lines 0-3   both players to the column of the blocks
;   decor       the pillars and torches of the title in
;               the colours of the screen: cold embers
;               for GAME OVER, bright flames for VICTORY
;   blocks      48 pixels wide: the crown (whole for GAME
;               OVER, the curse goes on; broken for
;               VICTORY), GAME and OVER or VICTORY, the
;               score. Its six digits are columns of 9
;               bytes in the Superchip RAM (main.asm:
;               end_score): the block reads them as it
;               reads its tables
;   the scene   lines 128-131 place the players; GAME
;               OVER: the Serpent King alone; VICTORY:
;               Sir Roderick and the pieces of the crown
; won (not 0: VICTORY) chooses the screen. Leaves through
; TO_MAIN, as the title.

; SCENE: the players of the scene ({1}: GO or VI): columns
; {1}_P0X, {1}_P1X, NUSIZ1 {1}_NUS1, REFP1 {1}_REF1, then
; SCN_H lines of the tables {1}_SK, _SKC (player 0) and
; {1}_SO, _SOC (player 1), bottom first
        MAC SCENE
        lda     #{1}_P0X
        ldx     #0
        jsr     e_place         ; line 128
        lda     #{1}_P1X
        ldx     #1
        jsr     e_place         ; line 129
        sta     WSYNC           ; line 130
        sta     HMOVE
        lda     #0
        sta     NUSIZ0
        sta     VDELP0
        sta     VDELP1
        sta     REFP0
        lda     #{1}_NUS1
        sta     NUSIZ1
        lda     #{1}_REF1
        sta     REFP1
        sta     HMCLR           ; 30: 27 cycles after HMOVE
        sta     WSYNC           ; line 131
        ldy     #SCN_H-1
.sc:    sta     WSYNC           ; lines 132-172
        lda     {1}_SK,y
        sta     GRP0            ;  6
        lda     {1}_SKC,y
        sta     COLUP0          ; 13
        lda     {1}_SO,y
        sta     GRP1            ; 20
        lda     {1}_SOC,y
        sta     COLUP1          ; 27
        dey
        bpl     .sc
        ENDM

ends_kernel:
        lda     #0
        sta     VBLANK          ; the picture starts
        sta     GRP0
        sta     GRP1
        sta     PF0
        sta     PF1
        sta     PF2
        sta     COLUBK
        IF TOP_BLANK
        ldy     #TOP_BLANK
ek_top: sta     WSYNC
        dey
        bne     ek_top
        ENDIF
        lda     #TITLE_X        ; lines 1-2: the players
        ldx     #0
        jsr     e_place
        lda     #TITLE_X+8
        ldx     #1
        jsr     e_place
        sta     WSYNC           ; line 3
        sta     HMOVE
        lda     #3
        sta     NUSIZ0
        sta     NUSIZ1
        lda     #1
        sta     VDELP0
        sta     VDELP1
        sta     CTRLPF
        lda     #0
        sta     REFP0
        sta     REFP1
        sta     HMCLR           ; 24 cycles after HMOVE
        lda     won
        beq     go_screen
        jmp     vi_screen

; GAME OVER
go_screen:
        DECOR   4, GOE_TOP, GO, E
        BLOCK   GOE             ; the crown
        DECOR   GOE_TOP+GOE_H, GOG_TOP, GO, E
        BLOCK   GOG             ; GAME
        DECOR   GOG_TOP+GOG_H, GOO_TOP, GO, E
        BLOCK   GOO             ; OVER
        DECOR   GOO_TOP+GOO_H, ESC_TOP, GO, E
        BLOCK   ESC             ; the score
        DECOR   ESC_TOP+ESC_H, SCN_SETUP, GO, E
        SCENE   GO              ; the Serpent King
        DECOR   SCN_SETUP+4+SCN_H, 192, GO, E
        jmp     ek_done

; VICTORY
vi_screen:
        DECOR   4, VIE_TOP, VI, E
        BLOCK   VIE             ; the crown broken
        DECOR   VIE_TOP+VIE_H, VIW_TOP, VI, E
        BLOCK   VIW             ; VICTORY
        DECOR   VIW_TOP+VIW_H, ESC_TOP, VI, E
        BLOCK   ESC             ; the score
        DECOR   ESC_TOP+ESC_H, SCN_SETUP, VI, E
        SCENE   VI              ; Sir Roderick, the pieces
        DECOR   SCN_SETUP+4+SCN_H, 192, VI, E

ek_done:
        sta     WSYNC           ; the first line after it
        lda     #0
        sta     PF0
        sta     PF1
        sta     PF2
        sta     COLUBK
        sta     VDELP0
        sta     VDELP1
        sta     GRP0
        sta     GRP1
        IF BOT_BLANK
        ldy     #BOT_BLANK
ek_bot: sta     WSYNC
        dey
        bne     ek_bot
        ENDIF
        lda     #2
        sta     VBLANK
        lda     #OVER_TIM
        sta     TIM64T
        jmp     TO_MAIN

; e_place: as t_place (title_kernel.asm), place (main.asm)
e_place:
        sta     WSYNC
        sec
ep_div: sbc     #15
        bcs     ep_div          ; (ep_div)
        eor     #7
        asl
        asl
        asl
        asl
        sta     HMP0,x
        sta     RESP0,x
        rts
