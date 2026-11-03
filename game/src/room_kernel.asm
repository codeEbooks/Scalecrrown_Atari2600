; room_kernel.asm - bank 0: the room
;
; Entered from the HUD (hud.asm, bank 7) in HUD line 28,
; when the players have their columns for the room. Lines {4}
;|; when Sir Roderick has his column for the room. Lines {1-3}
; 29-31 of the HUD (black) switch the ball on if the room {3}
; has a plug (it closes the outer opening of the rooms at {3}
; the ends of a level; the ball has the colour of the {3}
; playfield, the wall's) and read what the first line of {3}
; the room needs; then the 160 lines of the room, {3}
; BOT_BLANK {3}
;|; 29-31 of the HUD (black) read what the first line of the {1-2}
;|; room needs; then the 160 lines of the room, BOT_BLANK {1-2}
; black lines (PAL only); then the overscan starts and the
; program goes back to bank 7.
;
; Cycle counts in the comments: the cycle at which a store
; writes, counted from 0 at the start of the line; a "+" is
; a load that can take one cycle more when its address
; crosses a page.

room_kernel:
        sta     WSYNC           ; HUD line 29
        lda     plug            ; the ball: black on black {3}
        sta     ENABL           ; until the room starts {3}
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
        sta     PF2             ; unseen: COLUPF is 0 {4}
;|        sta     znpf2           ; for line A0 {1-3}
        sta     WSYNC           ; line 30
        lda     (kgfx),y        ; +
        tax
        lda     (sgfx),y        ; + {4}
        ldy     zt
        sta     WSYNC           ; line 31 stays empty
        jmp     k_top

; ---------------------------------------------------------
; The room: 20 courses of 8 lines, each four pairs of lines
; A and B. Lines A write the playfield colours, lines B the
; colours of the figures; both write the two figures. {4}
;|; colour of Sir Roderick; both write his figure. {1-3}
;
; At the start of each line (after WSYNC) the registers hold
; what the line writes first:
;   line A: A = GRP1, X = GRP0, Y = COLUPF {4}
;   line B: A = GRP1, X = GRP0, Y = COLUP0 {4}
;|;   line A: X = GRP0, Y = COLUPF {1-3}
;|;   line B: X = GRP0, Y = COLUP0 {1-3}
; The rest of the line prepares the next one; idx is the
; index (159 at the top) of the line being prepared.
; The playfield changes once a course: A1, A2, A3 read the
; next course from the Superchip RAM, A0 writes PF0 and {4}
; PF1, the end of B3 writes PF2 (after the right half is {4}
; drawn). {4}
;|; next course from the Superchip RAM, A0 writes PF0, PF1 {1-3}
;|; and PF2. {1-3}
; Lines B also write the colour of Sir Roderick to ENAM0: {2}
; bit 1 of it turns the blade (missile 0) on or off. Only in {2}
; the thrust can it show: otherwise RESMP0 keeps it hidden, {2}
; and in the thrust the colours are zero outside the figure {2}
; and have bit 1 only on the pair of the blade (art.py). {2}

        MAC LINE_A_REST         ; prepares line B
        ldy     idx
        dey
        sty     idx
        lda     (kcol),y        ; +
        sta     zt
        lda     (scol),y        ; + {4}
        sta     zc1 ; {4}
        lda     (kgfx),y        ; +
        tax
        lda     (sgfx),y        ; + {4}
        ldy     zt
        ENDM

        MAC LINE_B_FIRST
        sta     GRP1            ;  2 {4}
        stx     GRP0            ;  5 {4}
;|        stx     GRP0            ;  2 {1-3}
        sty     COLUP0          ;  8 {4}
;|        sty     COLUP0          ;  5 {1-3}
        sty     ENAM0           ; 11 the blade: bit 1 {4}
;|        sty     ENAM0           ;  8 the blade: bit 1 {2-3}
        lda     zc1 ; {4}
        sta     COLUP1          ; 17 {4}
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
        lda     (sgfx),y        ; + {4}
        ldy     zt
        ENDM

        MAC LINE_A_FIRST        ; A1-A3: {1} = SC table
        sta     GRP1            ;  2 {4}
        stx     GRP0            ;  5 {4}
;|        stx     GRP0            ;  2 {1-3}
        sty     COLUPF          ;  8 {4}
;|        sty     COLUPF          ;  5 {1-3}
        lda     zbk
        sta     COLUBK          ; 14 {4}
;|        sta     COLUBK          ; 11 {1-3}
        ldx     trow
        lda     SCR+{1},x
        ENDM

k_top:  sta     WSYNC
k_a0:   sta     GRP1            ;  2 {4}
;|k_a0:   stx     GRP0            ;  2 {1-3}
        stx     GRP0            ;  5 {4}
        sty     COLUPF          ;  8 {4}
;|        sty     COLUPF          ;  5 {1-3}
        lda     zbk
        sta     COLUBK          ; 14 {4}
;|        sta     COLUBK          ; 11 {1-3}
        lda     znpf0
        sta     PF0             ; 20 {4}
;|        sta     PF0             ; 17 {1-3}
        lda     znpf1
        sta     PF1             ; 26 {4}
;|        sta     PF1             ; 23 {1-3}
;|        lda     znpf2 {1-3}
;|        sta     PF2             ; 29 {1-3}
        LINE_A_REST
k_a0w:  sta     WSYNC           ; (the seam comes back here) {5}
;|        sta     WSYNC {1-4}
k_b0:   LINE_B_FIRST
        LINE_B_REST
        dec     trow            ; the next course
        sta     WSYNC
k_a1:   LINE_A_FIRST SC_PF0
        sta     znpf0
        LINE_A_REST
        sta     WSYNC
k_b1:   LINE_B_FIRST
        dec     zcnt            ; 30 the seam: this course? {5}
        bne     k_b1c           ; 33 (k_b1c) {5}
        jmp     k_seam          ; 35 {5}
k_b1c:  LINE_B_REST ; {5}
;|        LINE_B_REST {1-4}
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
        lda     (cbk),y         ; + (LINE_B_REST, with PF2 {4}
        sta     zbk             ; written from Y before Y {4}
        lda     (cpf),y         ; + gets its colour) {4}
        sta     zt ; {4}
        lda     (kgfx),y        ; + {4}
        tax ; {4}
        lda     (sgfx),y        ; + {4}
        ldy     znpf2 ; {4}
        nop ; {4}
        sty     PF2             ; 61+ after the right half {4}
        ldy     zt ; {4}
;|        LINE_B_REST {1-3}
        jmp     k_top

k_last: LINE_B_REST             ; course 19: lines A3, B3
        sta     WSYNC
        LINE_A_FIRST SC_PF2
        LINE_A_REST
        sta     WSYNC
        sta     GRP1            ; last line of the room {4}
        stx     GRP0 ; {4}
;|        stx     GRP0            ; last line of the room {1-3}
        sty     COLUP0
        sty     ENAM0 ; {2}
        lda     zc1 ; {4}
        sta     COLUP1 ; {4}
        sta     WSYNC
k_end:  lda     #0              ; first line after the room
        sta     ENABL           ;  4 the ball off (pixel 0 {3}
        sta     COLUBK          ;  7 is at clock 68) {3}
;|        sta     COLUBK          ;  4 (pixel 0: clock 68) {1-2}
        sta     GRP0
        sta     GRP1 ; {4}
        sta     PF0
        sta     PF1
        sta     PF2
        sta     ENAM0           ; the blade off {2}
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

; --------------------------------------------------------- {5}
; The seam: player 1 moves to the guard of the band {5}
; below. The count zcnt reaches 0 in line B1 of the course {5}
; c of the seam (main.asm: p1_bands); from there to the end {5}
; of line A0 of course c + 1 player 1 draws nothing, and {5}
; these lines do in turn what the kernel needs to move it: {5}
;   B1  (the rest)  prepares A2 as B1 does {5}
;   A2  reads PF1 and PF2 of course c + 1, prepares B2, {5}
;       REFP1 of the guard below {5}
;   B2  prepares A3 and the figure of Sir Roderick for B3 {5}
;   A3  waits zcoarse x 5 cycles, then RESP1: the coarse {5}
;       column (15 pixels per 5 cycles; RESP1 writes a cycle {5}
;       after place's, so the count and the fine move are {5}
;       place's for the column - 3) {5}
;   B3  HMOVE first: the fine move (HMP1, written in the HUD {5}
;       after HMCLR, SC_HM); its comb blanks pixels 0-7 of {5}
;       this line, which is the mortar of block column 0 {5}
;       (never in the courses of the openings); the pointer {5}
;       of the graphics of the guard below; PF2 of course {5}
;       c + 1 (in its window, after the right half) {5}
;   A0  as A0, and the pointer of the colours {5}
; then back to the end of A0, and the kernel goes on with {5}
; the guard below. Sir Roderick is drawn in every line. {5}

k_seam: lda     (cbk),y         ; + B1 (35) {5}
        sta     zbk ; {5}
        lda     (cpf),y         ; + {5}
        sta     zt ; {5}
        lda     (kgfx),y        ; + {5}
        tax ; {5}
        lda     #0              ; A2: no player 1 {5}
        ldy     zt ; {5}
        sta     WSYNC           ; 69 at most {5}
        sta     GRP1            ;  2 A2 {5}
        stx     GRP0            ;  5 {5}
        sty     COLUPF          ;  8 {5}
        lda     zbk ; {5}
        sta     COLUBK          ; 14 {5}
        ldx     trow ; {5}
        lda     SCR+SC_PF1,x ; {5}
        sta     znpf1 ; {5}
        lda     SCR+SC_PF2,x ; {5}
        sta     znpf2           ; 31 {5}
        ldy     idx ; {5}
        dey                     ; B2 {5}
        lda     (kcol),y        ; + {5}
        sta     zt ; {5}
        lda     (kgfx),y        ; + {5}
        tax ; {5}
        lda     zref ; {5}
        sta     REFP1           ; 57 (player 1 is empty) {5}
        dey                     ; A3 {5}
        sty     idx ; {5}
        lda     #0 ; {5}
        ldy     zt ; {5}
        sta     WSYNC           ; 72 at most {5}
        sta     GRP1            ;  2 B2 {5}
        stx     GRP0            ;  5 {5}
        sty     COLUP0          ;  8 {5}
        sty     ENAM0           ; 11 {5}
        ldy     idx             ; A3 {5}
        lda     (cbk),y         ; + {5}
        sta     zbk ; {5}
        lda     (cpf),y         ; + {5}
        sta     zt ; {5}
        lda     (kgfx),y        ; + {5}
        tax ; {5}
        dey                     ; B3: Sir Roderick {5}
        lda     (kgfx),y        ; + {5}
        sta     tmp ; {5}
        lda     (kcol),y        ; + {5}
        sta     zc1 ; {5}
        dey                     ; A0 of the next course {5}
        sty     idx ; {5}
        ldy     zt ; {5}
        lda     #0 ; {5}
        sta     WSYNC           ; 73 at most {5}
        sta     GRP1            ;  2 A3 {5}
        stx     GRP0            ;  5 {5}
        sty     COLUPF          ;  8 {5}
        lda     zbk ; {5}
        sta     COLUBK          ; 14 {5}
        ldx     zcoarse         ; 17 {5}
k_sdel: dex ; {5}
        bne     k_sdel          ; zcoarse x 5 - 1 (k_sdel) {5}
        sta     RESP1           ; 19 + 5 x zcoarse (24-69) {5}
        sta     WSYNC ; {5}
        sta     HMOVE           ;  2 B3: the fine move {5}
        ldx     tmp ; {5}
        stx     GRP0            ;  8 {5}
        ldy     zc1 ; {5}
        sty     COLUP0          ; 14 {5}
        sty     ENAM0           ; 17 (GRP1 is 0 since A3) {5}
        ldy     idx             ; A0 {5}
        lda     (cbk),y         ; + {5}
        sta     zbk ; {5}
        lda     (cpf),y         ; + {5}
        sta     zt ; {5}
        lda     (kgfx),y        ; + {5}
        tax ; {5}
        lda     s2gfx           ; the guard below {5}
        sta     sgfx ; {5}
        lda     s2gfx+1 ; {5}
        sta     sgfx+1 ; {5}
        ldy     znpf2 ; {5}
        sty     PF2             ; 61-64 {5}
        lda     #0 ; {5}
        ldy     zt ; {5}
        sta     WSYNC           ; 72 at most {5}
        sta     GRP1            ;  2 A0 {5}
        stx     GRP0            ;  5 {5}
        sty     COLUPF          ;  8 {5}
        lda     zbk ; {5}
        sta     COLUBK          ; 14 {5}
        lda     znpf0 ; {5}
        sta     PF0             ; 20 {5}
        lda     znpf1 ; {5}
        sta     PF1             ; 26 {5}
        ldy     idx ; {5}
        dey                     ; B0 {5}
        sty     idx ; {5}
        lda     (kcol),y        ; + {5}
        sta     zt ; {5}
        lda     (kgfx),y        ; + {5}
        tax ; {5}
        lda     s2col ; {5}
        sta     scol ; {5}
        lda     s2col+1 ; {5}
        sta     scol+1 ; {5}
        lda     #0 ; {5}
        ldy     zt ; {5}
        jmp     k_a0w           ; 71 at most: its WSYNC {5}
