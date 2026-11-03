; room_kernel.asm - bank 0: the room
;
; Entered from the HUD (hud.asm, bank 7) in HUD line 28,
; when the players have their columns for the room. Lines
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
        sta     PF2             ; unseen: COLUPF is 0
        sta     WSYNC           ; line 30
        lda     (kgfx),y        ; +
        tax
        lda     (sgfx),y        ; +
        ldy     zt
        sta     WSYNC           ; line 31 stays empty
        jmp     k_top

; ---------------------------------------------------------
; The room: 20 courses of 8 lines, each four pairs of lines
; A and B. Lines A write the playfield colours, lines B the
; colours of the figures; both write the two figures.
;
; At the start of each line (after WSYNC) the registers hold
; what the line writes first:
;   line A: A = GRP1, X = GRP0, Y = COLUPF
;   line B: A = GRP1, X = GRP0, Y = COLUP0
; The rest of the line prepares the next one; idx is the
; index (159 at the top) of the line being prepared.
; The playfield changes once a course: A1, A2, A3 read the
; next course from the Superchip RAM, A0 writes PF0 and
; PF1, the end of B3 writes PF2 (after the right half is
; drawn).
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
        lda     (scol),y        ; +
        sta     zc1
        lda     (kgfx),y        ; +
        tax
        lda     (sgfx),y        ; +
        ldy     zt
        ENDM

        MAC LINE_B_FIRST
        sta     GRP1            ;  2
        stx     GRP0            ;  5
        sty     COLUP0          ;  8
        sty     ENAM0           ; 11 the blade: bit 1
        lda     zc1
        sta     COLUP1          ; 17
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
        lda     (sgfx),y        ; +
        ldy     zt
        ENDM

        MAC LINE_A_FIRST        ; A1-A3: {1} = SC table
        sta     GRP1            ;  2
        stx     GRP0            ;  5
        sty     COLUPF          ;  8
        lda     zbk
        sta     COLUBK          ; 14
        ldx     trow
        lda     SCR+{1},x
        ENDM

k_top:  sta     WSYNC
k_a0:   sta     GRP1            ;  2
        stx     GRP0            ;  5
        sty     COLUPF          ;  8
        lda     zbk
        sta     COLUBK          ; 14
        lda     znpf0
        sta     PF0             ; 20
        lda     znpf1
        sta     PF1             ; 26
        LINE_A_REST
k_a0w:  sta     WSYNC           ; (the seam comes back here)
k_b0:   LINE_B_FIRST
        LINE_B_REST
        dec     trow            ; the next course
        sta     WSYNC
k_a1:   LINE_A_FIRST SC_PF0
        sta     znpf0
        LINE_A_REST
        sta     WSYNC
k_b1:   LINE_B_FIRST
        dec     zcnt            ; 30 the seam: this course?
        bne     k_b1c           ; 33 (k_b1c)
        jmp     k_seam          ; 35
k_b1c:  LINE_B_REST
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
        lda     (cbk),y         ; + (LINE_B_REST, with PF2
        sta     zbk             ; written from Y before Y
        lda     (cpf),y         ; + gets its colour)
        sta     zt
        lda     (kgfx),y        ; +
        tax
        lda     (sgfx),y        ; +
        ldy     znpf2
        nop
        sty     PF2             ; 61+ after the right half
        ldy     zt
        jmp     k_top

k_last: LINE_B_REST             ; course 19: lines A3, B3
        sta     WSYNC
        LINE_A_FIRST SC_PF2
        LINE_A_REST
        sta     WSYNC
        sta     GRP1            ; last line of the room
        stx     GRP0
        sty     COLUP0
        sty     ENAM0
        lda     zc1
        sta     COLUP1
        sta     WSYNC
k_end:  lda     #0              ; first line after the room
        sta     ENABL           ;  4 the ball off (pixel 0
        sta     COLUBK          ;  7 is at clock 68)
        sta     GRP0
        sta     GRP1
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

; ---------------------------------------------------------
; The seam: player 1 moves to the guard of the band
; below. The count zcnt reaches 0 in line B1 of the course
; c of the seam (main.asm: p1_bands); from there to the end
; of line A0 of course c + 1 player 1 draws nothing, and
; these lines do in turn what the kernel needs to move it:
;   B1  (the rest)  prepares A2 as B1 does
;   A2  reads PF1 and PF2 of course c + 1, prepares B2,
;       REFP1 of the guard below
;   B2  prepares A3 and the figure of Sir Roderick for B3
;   A3  waits zcoarse x 5 cycles, then RESP1: the coarse
;       column (15 pixels per 5 cycles; RESP1 writes a cycle
;       after place's, so the count and the fine move are
;       place's for the column - 3)
;   B3  HMOVE first: the fine move (HMP1, written in the HUD
;       after HMCLR, SC_HM); its comb blanks pixels 0-7 of
;       this line, which is the mortar of block column 0
;       (never in the courses of the openings); the pointer
;       of the graphics of the guard below; PF2 of course
;       c + 1 (in its window, after the right half)
;   A0  as A0, and the pointer of the colours
; then back to the end of A0, and the kernel goes on with
; the guard below. Sir Roderick is drawn in every line.

k_seam: lda     (cbk),y         ; + B1 (35)
        sta     zbk
        lda     (cpf),y         ; +
        sta     zt
        lda     (kgfx),y        ; +
        tax
        lda     #0              ; A2: no player 1
        ldy     zt
        sta     WSYNC           ; 69 at most
        sta     GRP1            ;  2 A2
        stx     GRP0            ;  5
        sty     COLUPF          ;  8
        lda     zbk
        sta     COLUBK          ; 14
        ldx     trow
        lda     SCR+SC_PF1,x
        sta     znpf1
        lda     SCR+SC_PF2,x
        sta     znpf2           ; 31
        ldy     idx
        dey                     ; B2
        lda     (kcol),y        ; +
        sta     zt
        lda     (kgfx),y        ; +
        tax
        lda     zref
        sta     REFP1           ; 57 (player 1 is empty)
        dey                     ; A3
        sty     idx
        lda     #0
        ldy     zt
        sta     WSYNC           ; 72 at most
        sta     GRP1            ;  2 B2
        stx     GRP0            ;  5
        sty     COLUP0          ;  8
        sty     ENAM0           ; 11
        ldy     idx             ; A3
        lda     (cbk),y         ; +
        sta     zbk
        lda     (cpf),y         ; +
        sta     zt
        lda     (kgfx),y        ; +
        tax
        dey                     ; B3: Sir Roderick
        lda     (kgfx),y        ; +
        sta     tmp
        lda     (kcol),y        ; +
        sta     zc1
        dey                     ; A0 of the next course
        sty     idx
        ldy     zt
        lda     #0
        sta     WSYNC           ; 73 at most
        sta     GRP1            ;  2 A3
        stx     GRP0            ;  5
        sty     COLUPF          ;  8
        lda     zbk
        sta     COLUBK          ; 14
        ldx     zcoarse         ; 17
k_sdel: dex
        bne     k_sdel          ; zcoarse x 5 - 1 (k_sdel)
        sta     WSYNC
        sta     HMOVE           ;  2 B3: the fine move
        ldx     tmp
        stx     GRP0            ;  8
        ldy     zc1
        sty     COLUP0          ; 14
        sty     ENAM0           ; 17 (GRP1 is 0 since A3)
        ldy     idx             ; A0
        lda     (cbk),y         ; +
        sta     zbk
        lda     (cpf),y         ; +
        sta     zt
        lda     (kgfx),y        ; +
        tax
        lda     s2gfx           ; the guard below
        sta     sgfx
        lda     s2gfx+1
        sta     sgfx+1
        ldy     znpf2
        sty     PF2             ; 61-64
        lda     #0
        ldy     zt
        sta     WSYNC           ; 72 at most
        sta     GRP1            ;  2 A0
        stx     GRP0            ;  5
        sty     COLUPF          ;  8
        lda     zbk
        sta     COLUBK          ; 14
        lda     znpf0
        sta     PF0             ; 20
        lda     znpf1
        sta     PF1             ; 26
        ldy     idx
        dey                     ; B0
        sty     idx
        lda     (kcol),y        ; +
        sta     zt
        lda     (kgfx),y        ; +
        tax
        lda     s2col
        sta     scol
        lda     s2col+1
        sta     scol+1
        lda     #0
        ldy     zt
        jmp     k_a0w           ; 71 at most: its WSYNC
