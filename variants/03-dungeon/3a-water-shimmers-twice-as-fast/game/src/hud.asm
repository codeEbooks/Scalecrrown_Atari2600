; hud.asm - bank 7: the HUD, 32 lines above the room
;
; Entered right after the WSYNC that ends the VBLANK, at
; cycle 3 of the first visible line. Draws TOP_BLANK black
; lines (PAL only), then the HUD:
;   lines 1-9    the six digits of the score
;   lines 12-15  the energy bar
;   lines 17-25  LEVEL n
;   lines 26-28  Sir Roderick to his column
; and goes on to bank 0 (room_kernel.asm) in line 28.
;
; Cycle counts in the comments: the cycle at which a store
; writes, counted from 0 at the start of the line.

hud:
        lda     #0
        sta     VBLANK          ; the picture starts
        IF TOP_BLANK
        ldy     #TOP_BLANK
hu_top: sta     WSYNC
        dey
        bne     hu_top
        ENDIF
        lda     #SCORE_COL      ; HUD line 0
        sta     COLUP0
        sta     COLUP1
        sta     WSYNC
        jsr     hud_digits      ; lines 1-9: the six digits
        sta     WSYNC           ; line 10
        lda     #0
        sta     GRP0
        sta     GRP1
        sta     GRP0            ; empty the delayed copies
        ldy     #3
        sta     WSYNC           ; line 11
        sta     WSYNC           ; line 12
hu_bar:                         ; lines 12-15: energy
        lda     BAR_COL,y
        sta     COLUPF          ;  6
        lda     bar1
        sta     PF1             ; 12
        lda     bar2
        sta     PF2             ; 18
        sta     WSYNC
        dey
        bpl     hu_bar
        lda     #0              ; line 16
        sta     PF1
        sta     PF2
        sta     COLUPF          ; the room's PF2 unseen
        lda     #TEXT_COL
        sta     COLUP0
        sta     COLUP1
        sta     WSYNC
        jsr     hud_text        ; lines 17-25: LEVEL n
        lda     kx
        sta     WSYNC           ; (the end of line 25)
        ; line 26: Sir Roderick to column kx, as place does
        ; it (the stores take 4 cycles, like sta HMP0,x)
        sec
hu_p0:  sbc     #15
        bcs     hu_p0           ; (hu_p0)
        eor     #7
        asl
        asl
        asl
        asl
        sta.w   HMP0
        sta.w   RESP0           ; 68 at most (kx <= 149)
        sta     WSYNC           ; 71 at most
        ; line 27: empty
        sta     WSYNC
        ; line 28: the fine moves, the room's settings
        sta     HMOVE           ;  2
        lda     kdir
        sta     REFP0
        lda     #0
        sta     VDELP0
        sta     VDELP1
        sta     COLUP0
        sta     GRP1            ; (the HUD may leave it on)
        lda     swnus
        sta     NUSIZ0          ; the width of the blade
        jmp     TO_ROOM         ; bank 0

; HUD48: 8 lines of 48 pixels, Y = 7 down to 0, the six
; columns read through six pointers: {1} ... {1}+10 (dig:
; the digits of the score; txp: the name of the level, in
; this bank). Called on the line before the first one.
; Both players are delayed (VDELP0, VDELP1) and have three
; copies 16 pixels apart:
; player 0 shows columns 1, 3, 5, player 1 columns 2, 4, 6.
; A delayed player shows the value written before the last
; write to the other player, so the four writes at the end
; change the copies on the right while the beam is between
; them.
        MAC HUD48
        ldy     #7
        sty     zt2
.loop:  lda     ({1}),y
        sta     GRP0            ; column 1 (waits)
        sta     WSYNC
        lda     ({1}+2),y
        sta     GRP1            ;  7 col 2; col 1 shows
        lda     ({1}+4),y
        sta     GRP0            ; 15 col 3; col 2 shows
        lda     ({1}+10),y
        sta     zt
        lda     ({1}+8),y
        tax
        lda     ({1}+6),y
        ldy     zt
        nop
        sta     GRP1            ; 43 col 4; col 3 shows
        stx     GRP0            ; 46 col 5; col 4 shows
        sty     GRP1            ; 49 col 6; col 5 shows
        sta     GRP0            ; 52 col 6 shows
        ldy     zt2
        dey
        sty     zt2
        bpl     .loop
        rts
        ENDM

; each routine in one page (as the blocks of the title: see
; title_kernel.asm); the padding comes after a jmp or an rts
HUD48_BYTES = 50

        IF (* & $FF00) != ((*+HUD48_BYTES) & $FF00)
        ALIGN   256
        ENDIF
hud_digits:
        HUD48   dig
        IF (* & $FF00) != ((*+HUD48_BYTES) & $FF00)
        ALIGN   256
        ENDIF
hud_text:
        HUD48   txp
