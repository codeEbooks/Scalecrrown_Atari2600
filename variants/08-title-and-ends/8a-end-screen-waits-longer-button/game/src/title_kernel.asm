; title_kernel.asm - bank 1: the title
;
; Entered right after the WSYNC that ends the VBLANK, at
; cycle 10 of the first visible line. 192 lines (PAL: 18
; black lines above and below):
;   lines 0-3     positions of the two players
;   decor lines   background, playfield colour and the
;                 playfield of the pillars and torches, one
;                 line of each table per line
;   three blocks  the crown and the two halves of the name,
;                 48 pixels wide, drawn with both players;
;                 the decor stays as on the line before
;   a fourth      the sound mode (MUSIC, SOUND FX, SILENT)
; Tables of the decor are from the top (index = line); the
; blocks are bottom first (index = lines left). The end
; screens (bank 6: ends_kernel.asm) use the same two
; macros with their own tables.

TITLE_X = 52                    ; column of the blocks

; DECOR: lines {1} to {2}-1; colours {3}_BG, {3}_PFC, the
; playfield {4}_PF0-2
        MAC DECOR
        ldx     #{1}
        ldy     {3}_BG+{1}
.dl:    sta     WSYNC
        sty     COLUBK          ;  2 (read the line before)
        lda     {3}_PFC,x
        sta     COLUPF          ;  9
        lda     {4}_PF0,x
        sta     PF0             ; 16
        lda     {4}_PF1,x
        sta     PF1             ; 23
        lda     {4}_PF2,x
        sta     PF2             ; 30
        inx
        ldy     {3}_BG,x        ; + the next line
        cpx     #{2}
        bne     .dl
        ENDM

; A block of 48 pixels: {1} the prefix of its tables.
; Both players delayed, three copies each (see the HUD in
; hud.asm); the colour of each line is written before the
; block starts on that line. The block stays in one page: a
; branch taken to another page takes a cycle more, and the
; end of the line has none to spare. When it would not fit,
; a jmp goes over to the next page.
BLOCK_BYTES = 60                ; a block, and a little more

        MAC BLOCK
        IF ((*+3) & $FF00) != ((*+3+BLOCK_BYTES) & $FF00)
        jmp     .go
        ALIGN   256
        ENDIF
.go:    ldy     #{1}_H-1
        sty     zt2
.bl:    lda     {1}0,y
        sta     GRP0            ; column 1 (waits)
        sta     WSYNC
        lda     {1}_COL,y
        sta     COLUP0          ;  6
        sta     COLUP1          ;  9
        lda     {1}1,y
        sta     GRP1            ; 16 col 2; col 1 shows
        lda     {1}2,y
        sta     GRP0            ; 23 col 3; col 2 shows
        ldx     {1}4,y
        lda     {1}5,y
        sta     zt
        lda     {1}3,y
        ldy     zt
        sta     GRP1            ; 44 col 4; col 3 shows
        stx     GRP0            ; 47 col 5; col 4 shows
        sty     GRP1            ; 50 col 6; col 5 shows
        sta     GRP0            ; 53 col 6 shows
        ldy     zt2
        dey
        sty     zt2
        bpl     .bl
        ENDM

title_kernel:
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
tk_top: sta     WSYNC
        dey
        bne     tk_top
        ENDIF
        lda     #TITLE_X        ; lines 1-2: the players
        ldx     #0
        jsr     t_place
        lda     #TITLE_X+8
        ldx     #1
        jsr     t_place
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
        DECOR   4, EMB_TOP, T, T
        BLOCK   EMB
        DECOR   EMB_TOP+EMB_H, SCA_TOP, T, T
        BLOCK   SCA
        DECOR   SCA_TOP+SCA_H, CRO_TOP, T, T
        BLOCK   CRO
        DECOR   CRO_TOP+CRO_H, MMU_TOP, T, T
        ; the sound mode (SELECT): a block for each, and the
        ; decor after it (a jmp after the block would use
        ; cycles that its last line has not)
        lda     mode
        beq     tm_go0
        lsr
        beq     tm_sfx
        jmp     tm_silent
tm_go0: jmp     tm_music
tm_sfx: BLOCK   MSF             ; SOUND FX
        DECOR   MSF_TOP+MSF_H, SCN_SETUP, T, T
        jmp     tm_done
tm_music:
        BLOCK   MMU             ; MUSIC
        DECOR   MMU_TOP+MMU_H, SCN_SETUP, T, T
        jmp     tm_done
tm_silent:
        BLOCK   MSI             ; SILENT
        DECOR   MSI_TOP+MSI_H, SCN_SETUP, T, T
tm_done:
        ; the duel: Sir Roderick and the Serpent King. Lines
        ; 128-131 place the players, the decor stays.
        lda     #SCN_KX
        ldx     #0
        jsr     t_place         ; line 128
        lda     #SCN_OX
        ldx     #1
        jsr     t_place         ; line 129
        sta     WSYNC           ; line 130
        sta     HMOVE
        lda     #0
        sta     NUSIZ0
        sta     VDELP0
        sta     VDELP1
        sta     REFP0
        lda     #5              ; the king twice as wide
        sta     NUSIZ1
        lda     #8              ; facing Sir Roderick
        sta     REFP1
        sta     HMCLR
        sta     WSYNC           ; line 131
        ldy     #SCN_H-1
scene:  sta     WSYNC           ; lines 132-172
        lda     SCN_K,y
        sta     GRP0            ;  6
        lda     SCN_KC,y
        sta     COLUP0          ; 13
        lda     SCN_O,y
        sta     GRP1            ; 20
        lda     SCN_OC,y
        sta     COLUP1          ; 27
        dey
        bpl     scene
        DECOR   SCN_SETUP+4+SCN_H, 192, T, T
        sta     WSYNC           ; first line after the title
        lda     #0
        sta     PF0
        sta     PF1
        sta     PF2
        sta     COLUBK
        sta     VDELP0
        sta     VDELP1
        IF BOT_BLANK
        ldy     #BOT_BLANK
tk_bot: sta     WSYNC
        dey
        bne     tk_bot
        ENDIF
        lda     #2
        sta     VBLANK
        lda     #OVER_TIM
        sta     TIM64T
        jmp     TO_MAIN

t_place:
        sta     WSYNC
        sec
tp_div: sbc     #15
        bcs     tp_div          ; (tp_div)
        eor     #7
        asl
        asl
        asl
        asl
        sta     HMP0,x
        sta     RESP0,x
        rts
