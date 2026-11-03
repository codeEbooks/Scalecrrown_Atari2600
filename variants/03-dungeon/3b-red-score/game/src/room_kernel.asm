; room_kernel.asm - bank 0: the room
;
; Entered from the HUD (hud.asm, bank 7) in HUD line 28,
; when Sir Roderick has his column for the room. Lines
; 29-31 of the HUD (black) switch the ball on if the room
; has a plug (it closes the outer opening of the rooms at
; the ends of a level; the ball has the colour of the
; playfield, the wall's) and read what the first line of
; the room needs; then the 160 lines of the room,
; BOT_BLANK
; black lines (PAL only); then the overscan starts and the
; program goes back to bank 7.
;
; Cycle counts in the comments: the cycle at which a store
; writes, counted from 0 at the start of the line; a "+" is
; a load that can take one cycle more when its address
; crosses a page.

room_kernel:
        sta     WSYNC           ; HUD line 29
        lda     plug            ; the ball: black on black
        sta     ENABL           ; until the room starts
        ldy     #159            ; what line A0 of course 0
        sty     idx             ; needs
        lda     #19
        sta     trow
        lda     (cbk),y         ; +
        sta     zbk             ; COLUBK of pair 0
        lda     (cpf),y         ; +
        sta     zt              ; COLUPF of pair 0
        lda     SCR+SC_PF0+19   ; course 0
        sta     znpf0
        lda     SCR+SC_PF1+19
        sta     znpf1
        lda     SCR+SC_PF2+19
        sta     znpf2           ; for line A0
        sta     WSYNC           ; line 30
        lda     (kgfx),y        ; +
        tax
        ldy     zt
        sta     WSYNC           ; line 31 stays empty
        jmp     k_top

; ---------------------------------------------------------
; The room: 20 courses of 8 lines, each four pairs of lines
; A and B. Lines A write the playfield colours, lines B the
; colour of Sir Roderick; both write his figure.
;
; At the start of each line (after WSYNC) the registers hold
; what the line writes first:
;   line A: X = GRP0, Y = COLUPF
;   line B: X = GRP0, Y = COLUP0
; The rest of the line prepares the next one; idx is the
; index (159 at the top) of the line being prepared.
; The playfield changes once a course: A1, A2, A3 read the
; next course from the Superchip RAM, A0 writes PF0, PF1
; and PF2.
; Lines B also write the colour of Sir Roderick to ENAM0:
; bit 1 of it turns the blade (missile 0) on or off. Only in
; the thrust can it show: otherwise RESMP0 keeps it hidden,
; and in the thrust the colours are zero outside the figure
; and have bit 1 only on the pair of the blade (art.py).

        MAC LINE_A_REST         ; prepares line B
        ldy     idx
        dey
        sty     idx
        lda     (kcol),y        ; +
        sta     zt
        lda     (kgfx),y        ; +
        tax
        ldy     zt
        ENDM

        MAC LINE_B_FIRST
        stx     GRP0            ;  2
        sty     COLUP0          ;  5
        sty     ENAM0           ;  8 the blade: bit 1
        ldy     idx
        dey
        sty     idx
        ENDM

        MAC LINE_B_REST         ; prepares line A
        lda     (cbk),y         ; +
        sta     zbk
        lda     (cpf),y         ; +
        sta     zt
        lda     (kgfx),y        ; +
        tax
        ldy     zt
        ENDM

        MAC LINE_A_FIRST        ; A1-A3: {1} = SC table
        stx     GRP0            ;  2
        sty     COLUPF          ;  5
        lda     zbk
        sta     COLUBK          ; 11
        ldx     trow
        lda     SCR+{1},x
        ENDM

k_top:  sta     WSYNC
k_a0:   stx     GRP0            ;  2
        sty     COLUPF          ;  5
        lda     zbk
        sta     COLUBK          ; 11
        lda     znpf0
        sta     PF0             ; 17
        lda     znpf1
        sta     PF1             ; 23
        lda     znpf2
        sta     PF2             ; 29
        LINE_A_REST
        sta     WSYNC
k_b0:   LINE_B_FIRST
        LINE_B_REST
        dec     trow            ; the next course
        sta     WSYNC
k_a1:   LINE_A_FIRST SC_PF0
        sta     znpf0
        LINE_A_REST
        sta     WSYNC
k_b1:   LINE_B_FIRST
        LINE_B_REST
        sta     WSYNC
k_a2:   LINE_A_FIRST SC_PF1
        sta     znpf1
        LINE_A_REST
        sta     WSYNC
k_b2:   LINE_B_FIRST
        lda     trow
        bmi     k_last          ; past the last course
        LINE_B_REST
        sta     WSYNC
k_a3:   LINE_A_FIRST SC_PF2
        sta     znpf2
        LINE_A_REST
        sta     WSYNC
k_b3:   LINE_B_FIRST
        LINE_B_REST
        jmp     k_top

k_last: LINE_B_REST             ; course 19: lines A3, B3
        sta     WSYNC
        LINE_A_FIRST SC_PF2
        LINE_A_REST
        sta     WSYNC
        stx     GRP0            ; last line of the room
        sty     COLUP0
        sty     ENAM0
        sta     WSYNC
k_end:  lda     #0              ; first line after the room
        sta     ENABL           ;  4 the ball off (pixel 0
        sta     COLUBK          ;  7 is at clock 68)
        sta     GRP0
        sta     PF0
        sta     PF1
        sta     PF2
        sta     ENAM0           ; the blade off
        IF BOT_BLANK
        ldy     #BOT_BLANK
k_bot:  sta     WSYNC
        dey
        bne     k_bot
        ENDIF
        lda     #2
        sta     VBLANK
        lda     #OVER_TIM
        sta     TIM64T
        jmp     TO_MAIN
