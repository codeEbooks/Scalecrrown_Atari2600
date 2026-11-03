; hud.asm - bank 7: the HUD, 32 lines above the room
;
; Entered right after the WSYNC that ends the VBLANK, at
; cycle 3 of the first visible line. Draws TOP_BLANK black
; lines (PAL only), then the HUD:
;   lines 1-9    the six digits of the score {3}
;   lines 12-15  the energy bar {3}
;   lines 17-25  LEVEL n {3}
;|;   lines 0-25   black {1-2}
;   lines 26-28  Sir Roderick and player 1 to their columns {4}
;                (player 1: the thing of band A; the fine {5}
;                move of the seam waits in HMP1) {5}
;|;                (player 1: the thing of the room) {4-4}
;|;   lines 26-28  Sir Roderick to his column {1-3}
; and goes on to bank 0 (room_kernel.asm) in line 28, or to {6}
; bank 2 (throne_kernel.asm) in the throne room. {6}
;|; and goes on to bank 0 (room_kernel.asm) in line 28. {1-5}
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
;|        ldy     #25             ; lines 0-24: black {1-2}
;|hu_black: {1-2}
;|        sta     WSYNC {1-2}
;|        dey {1-2}
;|        bne     hu_black {1-2}
        lda     #SCORE_COL      ; HUD line 0 {3}
        sta     COLUP0 ; {3}
        sta     COLUP1 ; {3}
        sta     WSYNC ; {3}
        jsr     hud_digits      ; lines 1-9: the six digits {3}
        sta     WSYNC           ; line 10 {3}
        lda     #0 ; {3}
        sta     GRP0 ; {3}
        sta     GRP1 ; {3}
        sta     GRP0            ; empty the delayed copies {3}
        ldy     #3 ; {3}
        sta     WSYNC           ; line 11 {3}
        sta     WSYNC           ; line 12 {3}
hu_bar:                         ; lines 12-15: energy {3}
        lda     BAR_COL,y ; {3}
        sta     COLUPF          ;  6 {3}
        lda     bar1 ; {3}
        sta     PF1             ; 12 {3}
        lda     bar2 ; {3}
        sta     PF2             ; 18 {3}
        sta     WSYNC ; {3}
        dey ; {3}
        bpl     hu_bar ; {3}
        lda     #0              ; line 16 {3}
        sta     PF1 ; {3}
        sta     PF2 ; {3}
        sta     COLUPF          ; the room's PF2 unseen {3}
        lda     #TEXT_COL ; {3}
        sta     COLUP0 ; {3}
        sta     COLUP1 ; {3}
        sta     WSYNC ; {3}
        jsr     hud_text        ; lines 17-25: LEVEL n {3}
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
        lda     ox ; {4}
        sta     WSYNC           ; 73 at most {4}
;|        sta     WSYNC           ; 71 at most {1-3}
        ; line 27: player 1 to column ox {4}
        sec ; {4}
hu_p1:  sbc     #15 ; {4}
        bcs     hu_p1           ; (hu_p1) {4}
        eor     #7 ; {4}
        asl ; {4}
        asl ; {4}
        asl ; {4}
        asl ; {4}
        sta.w   HMP1 ; {4}
        sta.w   RESP1 ; {4}
;|        ; line 27: empty {1-3}
        sta     WSYNC
        ; line 28: the fine moves, the room's settings
        sta     HMOVE           ;  2
        lda     kdir
        sta     REFP0
        lda     odir ; {4}
        sta     REFP1 ; {4}
        lda     #0
        sta     VDELP0 ; {3}
        sta     VDELP1 ; {3}
        sta     COLUP0
        sta     COLUP1 ; {4}
;|        sta     GRP1            ; (the HUD may leave it on) {3-3}
        lda     swnus ; {2}
        sta     NUSIZ0          ; the width of the blade {2}
        lda     onus ; {4}
        sta     NUSIZ1 ; {4}
        sta     HMCLR           ; 43: 41 cycles after HMOVE {5}
        lda     SCR+SC_HM       ; the fine move of the seam {5}
        sta     HMP1            ; (its HMOVE uses it) {5}
        lda     room            ; the throne room has its {6}
        cmp     #THRONE_ROOM    ; own kernel {6}
        beq     hu_throne ; {6}
        jmp     TO_ROOM         ; bank 0
hu_throne: ; {6}
        jmp     TO_THRONE       ; bank 2 {6}

; HUD48: 8 lines of 48 pixels, Y = 7 down to 0, the six {3}
; columns read through six pointers: {1} ... {1}+10 (dig: {3}
; the digits of the score; txp: the name of the level, in {3}
; this bank). Called on the line before the first one. {3}
; Both players are delayed (VDELP0, VDELP1) and have three {3}
; copies 16 pixels apart: {3}
; player 0 shows columns 1, 3, 5, player 1 columns 2, 4, 6. {3}
; A delayed player shows the value written before the last {3}
; write to the other player, so the four writes at the end {3}
; change the copies on the right while the beam is between {3}
; them. {3}
        MAC HUD48 ; {3}
        ldy     #7 ; {3}
        sty     zt2 ; {3}
.loop:  lda     ({1}),y ; {3}
        sta     GRP0            ; column 1 (waits) {3}
        sta     WSYNC ; {3}
        lda     ({1}+2),y ; {3}
        sta     GRP1            ;  7 col 2; col 1 shows {3}
        lda     ({1}+4),y ; {3}
        sta     GRP0            ; 15 col 3; col 2 shows {3}
        lda     ({1}+10),y ; {3}
        sta     zt ; {3}
        lda     ({1}+8),y ; {3}
        tax ; {3}
        lda     ({1}+6),y ; {3}
        ldy     zt ; {3}
        nop ; {3}
        sta     GRP1            ; 43 col 4; col 3 shows {3}
        stx     GRP0            ; 46 col 5; col 4 shows {3}
        sty     GRP1            ; 49 col 6; col 5 shows {3}
        sta     GRP0            ; 52 col 6 shows {3}
        ldy     zt2 ; {3}
        dey ; {3}
        sty     zt2 ; {3}
        bpl     .loop ; {3}
        rts ; {3}
        ENDM ; {3}

; each routine in one page (as the blocks of the title: see {3}
; title_kernel.asm); the padding comes after a jmp or an rts {3}
HUD48_BYTES = 50 ; {3}

        IF (* & $FF00) != ((*+HUD48_BYTES) & $FF00) ; {3}
        ALIGN   256 ; {3}
        ENDIF ; {3}
hud_digits: ; {3}
        HUD48   dig ; {3}
        IF (* & $FF00) != ((*+HUD48_BYTES) & $FF00) ; {3}
        ALIGN   256 ; {3}
        ENDIF ; {3}
hud_text: ; {3}
        HUD48   txp ; {3}
