; throne_kernel.asm - bank 2: the throne room
;
; The room kernel of bank 0 (room_kernel.asm) for the last
; room, with two changes:
; - no seam: player 1 shows one thing, the Serpent King
;   (twice as wide) or the crown (four times as wide);
; - the venom: missile 1. Lines B write the colour of player
;   1 to ENAM1 as well as to COLUP1: bit 1 of it turns the
;   missile on or off, as bit 1 of Sir Roderick's colour
;   does with the blade (missile 0). While the venom flies,
;   the King's colours have bit 1 only on the pair of his
;   mouth (look.king_colours; the tables are padded with
;   zeros, because the kernel reads them on every line), so
;   the venom is drawn on those two lines, at the column of
;   missile 1 (prep_room); otherwise RESMP1 keeps it hidden.
; Sir Roderick's figures and colours are the same bytes at
; the same place as in bank 0 (kfig2.asm, kfig0.asm): the
; pointers of prep_room work in both banks. Entered from the
; HUD (hud.asm, bank 7) in HUD line 28, as the room kernel;
; leaves through TO_MAIN in the same way.
;
; Cycle counts in the comments: the cycle at which a store
; writes, counted from 0 at the start of the line; a "+" is
; a load that can take one cycle more when its address
; crosses a page (the colour table of the room is in one
; page: its two loads never do).

throne_kernel:
        sta     WSYNC           ; HUD line 29
        lda     plug            ; the ball: black on black
        sta     ENABL           ; until the room starts
        ldy     #159            ; what line A0 of course 0
        sty     idx             ; needs
        lda     #19
        sta     trow
        lda     (cbk),y
        sta     zbk             ; COLUBK of pair 0
        lda     (cpf),y
        sta     zt              ; COLUPF of pair 0
        lda     SCR+SC_PF0+19   ; course 0
        sta     znpf0
        lda     SCR+SC_PF1+19
        sta     znpf1
        lda     SCR+SC_PF2+19
        sta     PF2             ; unseen: COLUPF is 0
        sta     WSYNC           ; line 30
        lda     (kgfx),y        ; +
        tax
        lda     (sgfx),y        ; +
        ldy     zt
        sta     WSYNC           ; line 31 stays empty
        jmp     t_top

; ---------------------------------------------------------
; The room: 20 courses of 8 lines, four pairs of lines A and
; B each, as in room_kernel.asm (the same macros, with
; ENAM1).

        MAC TLINE_A_REST        ; prepares line B
        ldy     idx
        dey
        sty     idx
        lda     (kcol),y        ; +
        sta     zt
        lda     (scol),y        ; +
        sta     zc1
        lda     (kgfx),y        ; +
        tax
        lda     (sgfx),y        ; +
        ldy     zt
        ENDM

        MAC TLINE_B_FIRST
        sta     GRP1            ;  2
        stx     GRP0            ;  5
        sty     COLUP0          ;  8
        sty     ENAM0           ; 11 the blade: bit 1
        lda     zc1
        sta     COLUP1          ; 17
        sta     ENAM1           ; 20 the venom: bit 1
        ldy     idx
        dey
        sty     idx
        ENDM

        MAC TLINE_B_REST        ; prepares line A
        lda     (cbk),y
        sta     zbk
        lda     (cpf),y
        sta     zt
        lda     (kgfx),y        ; +
        tax
        lda     (sgfx),y        ; +
        ldy     zt
        ENDM

        MAC TLINE_A_FIRST       ; A1-A3: {1} = SC table
        sta     GRP1            ;  2
        stx     GRP0            ;  5
        sty     COLUPF          ;  8
        lda     zbk
        sta     COLUBK          ; 14
        ldx     trow
        lda     SCR+{1},x
        ENDM

t_top:  sta     WSYNC
        sta     GRP1            ;  2 A0
        stx     GRP0            ;  5
        sty     COLUPF          ;  8
        lda     zbk
        sta     COLUBK          ; 14
        lda     znpf0
        sta     PF0             ; 20
        lda     znpf1
        sta     PF1             ; 26
        TLINE_A_REST
        sta     WSYNC
        TLINE_B_FIRST           ; B0
        TLINE_B_REST
        dec     trow            ; the next course
        sta     WSYNC
        TLINE_A_FIRST SC_PF0    ; A1
        sta     znpf0
        TLINE_A_REST
        sta     WSYNC
        TLINE_B_FIRST           ; B1
        TLINE_B_REST
        sta     WSYNC
        TLINE_A_FIRST SC_PF1    ; A2
        sta     znpf1
        TLINE_A_REST
        sta     WSYNC
        TLINE_B_FIRST           ; B2
        lda     trow
        bmi     t_last          ; past the last course
        TLINE_B_REST
        sta     WSYNC
        TLINE_A_FIRST SC_PF2    ; A3
        sta     znpf2
        TLINE_A_REST
        sta     WSYNC
        TLINE_B_FIRST           ; B3
        lda     (cbk),y         ; (TLINE_B_REST, with PF2
        sta     zbk             ; written from Y before Y
        lda     (cpf),y         ; gets its colour)
        sta     zt
        lda     (kgfx),y        ; +
        tax
        lda     (sgfx),y        ; +
        ldy     znpf2
        sty     PF2             ; 62+ after the right half
        ldy     zt
        jmp     t_top

t_last: TLINE_B_REST            ; course 19: lines A3, B3
        sta     WSYNC
        TLINE_A_FIRST SC_PF2
        TLINE_A_REST
        sta     WSYNC
        sta     GRP1            ; last line of the room
        stx     GRP0
        sty     COLUP0
        sty     ENAM0
        lda     zc1
        sta     COLUP1
        sta     ENAM1
        sta     WSYNC
        lda     #0              ; first line after the room
        sta     ENABL           ;  4 the ball off (pixel 0
        sta     COLUBK          ;  7 is at clock 68)
        sta     GRP0
        sta     GRP1
        sta     PF0
        sta     PF1
        sta     PF2
        sta     ENAM0           ; the blade off
        sta     ENAM1           ; the venom off
        IF BOT_BLANK
        ldy     #BOT_BLANK
t_bot:  sta     WSYNC
        dey
        bne     t_bot
        ENDIF
        lda     #2
        sta     VBLANK
        lda     #OVER_TIM
        sta     TIM64T
        jmp     TO_MAIN
