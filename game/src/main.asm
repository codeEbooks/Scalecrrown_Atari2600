; main.asm - bank 7: start, the frame, and what is done
; in it besides the kernels:
; - the title, SELECT, the end screens (bank 6) and their {8}
;   songs; {8}
; - the buttons: RESET starts again; {2}
;|; - SELECT in the game: the next sound mode; {7-7}
; - GAME OVER, VICTORY; {8}
;|; - GAME OVER: the game stops; {5-5}
;|; - GAME OVER, VICTORY: the game stops; {6-7}
; - setting a room up: its playfield comes from bank 3
;   into the Superchip RAM;
; - what the kernels need: Sir Roderick, the colours of
;   the room, the HUD, the bands of player 1, the King or {6}
;   the crown on player 1, the venom on missile 1. {6}
;|;   the room, the HUD, the bands of player 1. {5-5}
;|;   the room, the HUD, player 1. {4-4}
;|;   the room, the HUD. {3-3}
;|;   the room. {1-2}
; In the overscan the things of the room, the guards and {6}
; the Serpent King (bank 4, in a game) and the sound {7}
; player (bank 5). {7}
;|; the Serpent King (bank 4). {6-6}
;|; In the overscan the things of the room and the guards {5-5}
;|; (bank 4). {5-5}
;|; In the overscan the things of the room (bank 4). {4-4}

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
;|        jsr     new_game        ; the game at once {1-7}
        jmp     main

kernel_done:                    ; back from a kernel (the
                                ; overscan timer is running)
        lda     screen          ; the title, an end screen: {8}
        beq     kd_sound        ; only the sound {8}
        jsr     TO_THINGS       ; the things (bank 4) {4}
        jsr     digits          ; the score's digits {3}
kd_sound:                       ; the sound (bank 5) {7}
        jsr     TO_SOUND ; {7}
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
        jsr     buttons ; {2}
        lda     screen ; {8}
        bne     fr_game ; {8}
        lda     over            ; screen 0 and over {8}
        ora     won             ; or won: an end screen {8}
        bne     fr_ends ; {8}
        lda     pressed         ; the title: SELECT chooses {8}
        and     #$02            ; the next sound mode {8}
        beq     fr_start ; {8}
        ldx     mode ; {8}
        inx ; {8}
        cpx     #3 ; {8}
        bcc     fr_mode ; {8}
        ldx     #0 ; {8}
fr_mode: ; {8}
        stx     mode ; {8}
fr_start: ; {8}
        lda     pressed         ; the button or RESET starts {8}
        and     #$81            ; a game {8}
        bne     fr_new ; {8}
        jmp     fr_title ; {8}
fr_new: jsr     new_game ; {8}
        jmp     fr_room ; {8}
fr_game: ; {2}
;|        lda     pressed         ; SELECT: the next sound {7-7}
;|        and     #$02            ; mode {7-7}
;|        beq     fr_reset {7-7}
;|        ldx     mode {7-7}
;|        inx {7-7}
;|        cpx     #3 {7-7}
;|        bcc     fr_mode {7-7}
;|        ldx     #0 {7-7}
;|fr_mode: {7-7}
;|        stx     mode {7-7}
;|fr_reset: {7-7}
        lda     pressed ; {2}
        lsr                     ; bit 0: RESET {2}
        bcc     fr_play ; {2}
        jsr     new_game        ; start again {2}
        jmp     fr_room ; {2}
fr_play: ; {2}
        lda     won             ; VICTORY: nothing moves {6}
        beq     fr_over ; {6}
        cmp     #VIC_FRAMES     ; for VIC_FRAMES, then the {8}
        bcs     fr_end          ; end screen {8}
        inc     won ; {8}
        bne     fr_room         ; (never 0) {6}
fr_over: ; {5}
        lda     over            ; GAME OVER: the same, {6}
;|        lda     over            ; GAME OVER: nothing moves {5-5}
        beq     fr_knight ; {5}
        cmp     #GO_FRAMES      ; for GO_FRAMES {8}
        bcs     fr_end ; {8}
        inc     over ; {8}
        bne     fr_room         ; (never 0) {5}
fr_end: lda     #0              ; the end screen: screen 0, {8}
        sta     screen          ; over or won go on counting {8}
fr_ends: ; {8}
        lda     pressed         ; RESET: a game at once {8}
        lsr ; {8}
        bcc     fe_count ; {8}
        jsr     new_game ; {8}
        jmp     fr_room ; {8}
fe_count: ; {8}
        lda     won             ; END_FRAMES more, then the {8}
        beq     fe_over         ; button {8}
        cmp     #VIC_FRAMES+END_FRAMES ; {8}
        bcs     fe_button ; {8}
        inc     won ; {8}
        bne     fe_draw         ; (never 0) {8}
fe_over: ; {8}
        lda     over ; {8}
        cmp     #GO_FRAMES+END_FRAMES ; {8}
        bcs     fe_button ; {8}
        inc     over ; {8}
        bne     fe_draw         ; (never 0) {8}
fe_button: ; {8}
        bit     pressed         ; the button: the title, the {8}
        bpl     fe_draw         ; theme from its start {8}
        lda     #0 ; {8}
        sta     over ; {8}
        sta     won ; {8}
        jsr     theme ; {8}
        jmp     fr_title ; {8}
fe_draw: ; {8}
        jsr     end_score       ; the digits for the screen {8}
        lda     #$FF ; {8}
        sta     shown           ; set the room up again {8}
fe_wait:                        ; the tests read INTIM here {8}
        lda     INTIM ; {8}
        bne     fe_wait ; {8}
        sta     WSYNC ; {8}
        jmp     TO_ENDS         ; bank 6 {8}
fr_knight: ; {2}
        jsr     knight          ; Sir Roderick (knight.asm) {2}
fr_room:
        jsr     setup_room
        jsr     room_state ; {2}
        jsr     p1_bands ; {4}
        jsr     prep_room
vb_end:                         ; the tests read INTIM here
        lda     INTIM
        bne     vb_end
        sta     WSYNC
        jmp     hud             ; HUD (hud.asm), then room

fr_title: ; {8}
        lda     #$FF ; {8}
        sta     shown           ; set the room up again {8}
vb_wait: ; {8}
        lda     INTIM ; {8}
        bne     vb_wait ; {8}
        sta     WSYNC ; {8}
        jmp     TO_TITLE ; {8}

; --------------------------------------------------------- {2}
; buttons: pressed = down in this frame and up in the one {2}
; before; fire $80, SELECT $02, RESET $01 (all are 0 when {2}
; down) {2}

buttons: ; {2}
        lda     INPT4           ; bit 7: the fire button {2}
        eor     #$FF ; {2}
        and     #$80 ; {2}
        sta     tmp ; {2}
        lda     SWCHB           ; bit 0 RESET, bit 1 SELECT {2}
        eor     #$FF ; {2}
        and     #$03 ; {2}
        ora     tmp ; {2}
        tax                     ; down now {2}
        eor     held            ; changed {2}
        stx     held ; {2}
        and     held            ; changed and down now {2}
        sta     pressed ; {2}
        rts ; {2}

; --------------------------------------------------------- {7}
; theme: the theme from its first step; the player {7}
; silences what was playing (a new song: smode $FF) {7}

theme:  lda     #SONG_THEME ; {7}
        sta     song ; {7}
        lda     #$FF ; {7}
        sta     smode ; {7}
        rts ; {7}

; end_score: the six digits of the score into the {8}
; Superchip RAM for the end screen (bank 6): column k at {8}
; 9 k, bottom first as the tables of a block: byte 0 empty, {8}
; bytes 1-8 the digit (DIGITS is bottom first too) {8}

end_score: ; {8}
        ldx     #0              ; X: the column's byte {8}
        stx     tmp+1           ; the digit, 0-5 {8}
es_dig: lda     tmp+1 ; {8}
        lsr                     ; C: an odd digit {8}
        tay ; {8}
        lda     score,y ; {8}
        bcs     es_lo           ; odd: the low nibble {8}
        lsr ; {8}
        lsr ; {8}
        lsr ; {8}
        lsr ; {8}
es_lo:  and     #$0F ; {8}
        asl ; {8}
        asl ; {8}
        asl ; {8}
        tay                     ; 8 x the digit {8}
        lda     #0 ; {8}
        sta     SCW,x           ; the empty line {8}
        lda     #8 ; {8}
        sta     tmp ; {8}
es_byte: ; {8}
        inx ; {8}
        lda     DIGITS,y ; {8}
        sta     SCW,x ; {8}
        iny ; {8}
        dec     tmp ; {8}
        bne     es_byte ; {8}
        inx                     ; the next column {8}
        inc     tmp+1 ; {8}
        lda     tmp+1 ; {8}
        cmp     #6 ; {8}
        bne     es_dig ; {8}
        rts ; {8}

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
        sta     kdist ; {2}
        sta     hacc ; {2}
        sta     vacc ; {2}
        sta     thrust ; {2}
        sta     score ; {3}
        sta     score+1 ; {3}
        sta     score+2 ; {3}
        sta     key             ; no key, all closed {4}
        sta     opened ; {4}
        sta     hurt            ; not hurt, playing {5}
        sta     over ; {5}
        sta     won             ; not won, no parry, the {6}
        sta     parry           ; King on his throne {6}
        sta     SCW+SC_CROWN ; {6}
        lda     #ENERGY_FULL ; {3}
        sta     energy ; {3}
        lda     #$FF
        sta     shown           ; the room is set up again
        jsr     theme           ; the theme anew {7}
        jmp     digits          ; (score 0) {3}
;|        rts {1-2}

; ---------------------------------------------------------
; setup_room: when the screen changes, the playfield of
; the room goes into the Superchip RAM (bank 3)
; - with its door open if it is; {4}
;|; - with its door open; {3-3}
; - the HUD gets the name of its level; the plug of the {3}
;   room is chosen; {3}
; - the plates of the spikes start down, NUSIZ1 of the {4}
;   room; {4}
; - the guards go to their start alive (the army is {5}
;   infinite); {5}
; - in the throne room the King starts again (in front {6}
;   of his throne, no blow, no venom; unless he has been {6}
;   beaten: the crown stays) {6}

setup_room:
        lda     screen
        cmp     shown
        beq     su_done
        sta     shown
        jsr     TO_COPY         ; bank 3: room_copy
su_copied:                      ; the tests time the copy
        lda     room            ; the name of the level {3}
        lsr ; {3}
        lsr ; {3}
        tax ; {3}
        jsr     name ; {3}
        lda     SU_DOWN,x       ; the plates: down, for the {4}
        sta     spk             ; time of the level {4}
        lda     #0 ; {4}
        sta     spup ; {4}
        sta     SCW+SC_ACC      ; the guards: no fraction, {5}
        sta     SCW+SC_SPR      ; no sprint, no stun, no {9}
        sta     SCW+SC_GT       ; return, {9}
        sta     SCW+SC_GT+1 ; {9}
        lda     #3              ; both alive, unwounded, {9}
;|        lda     #3              ; both alive, {5-8}
        sta     SCW+SC_LIVE ; {5}
        lda     #8              ; facing left, {5}
        sta     SCW+SC_SD ; {5}
        sta     SCW+SC_SD+1 ; {5}
        ldx     room ; {3}
        lda     S_X,x           ; at their start (the first: {5}
        sta     SCW+SC_SX       ; its coarse column and fine {5}
        lda     S_X+16,x        ; move for the seam, as {5}
        sta     SCW+SC_SX+1     ; things.asm keeps them) {5}
        lda     S_CO,x ; {5}
        sta     zcoarse ; {5}
        lda     S_HM,x ; {5}
        sta     SCW+SC_HM ; {5}
        cpx     #THRONE_ROOM ; {6}
        bne     su_plug ; {6}
        lda     #KING_START     ; the King {6}
        sta     SCW+SC_KT ; {6}
        lda     #0 ; {6}
        sta     SCW+SC_KH ; {6}
        sta     SCW+SC_KF ; {6}
        sta     SCW+SC_VD ; {6}
        sta     SCW+SC_VA ; {6}
        lda     #SPIT_FIRST ; {6}
        sta     SCW+SC_KS ; {6}
su_plug: ; {3}
        lda     PLUG,x          ; the ball on or off {3}
        sta     plug ; {3}
        lda     OB_NUS,x ; {4}
        sta     onus ; {4}
su_done:
        rts

; name: the six pointers of the name in the HUD, X = 0-3 {3}
; the level - 1, 4 GAME OVER: one a column of 8 bytes, the {3}
; sixth 40 bytes after the first (room_state adds 8 for the {3}
; key); the 56 bytes are in one page: one high byte {3}
name:   lda     TX_HI,x ; {3}
        sta     txp+1 ; {3}
        sta     txp+3 ; {3}
        sta     txp+5 ; {3}
        sta     txp+7 ; {3}
        sta     txp+9 ; {3}
        sta     txp+11 ; {3}
        lda     TX_LO,x ; {3}
        sta     txp ; {3}
        clc                     ; (no carry: one page) {3}
        adc     #8 ; {3}
        sta     txp+2 ; {3}
        adc     #8 ; {3}
        sta     txp+4 ; {3}
        adc     #8 ; {3}
        sta     txp+6 ; {3}
        adc     #8 ; {3}
        sta     txp+8 ; {3}
        adc     #8 ; {3}
        sta     txp+10 ; {3}
        rts ; {3}

; --------------------------------------------------------- {2}
;{2}
; room_state: in every frame of a game, what follows from
; the things of the room (things.asm, bank 4, in the {4}
; overscan): the thing of player 1 closed or open, the {4}
; collision map with the door closed or open, the HUD {4}
; with the key after LEVEL n (the sixth column of the {4}
; name, 8 bytes on) or, after the end, GAME OVER or {6}
; VICTORY {6}
;|; name, 8 bytes on) or, after the end, GAME OVER {5-5}
;|; name, 8 bytes on) {4-4}
;|; the room: its collision map {2-3}

room_state: ; {2}
        ldx     room ; {2}
        ldy     OB_KIND0,x      ; the thing: closed {4}
        lda     OB_BIT,x ; {4}
        and     opened ; {4}
        beq     rs_kind ; {4}
        ldy     OB_KIND1,x      ; open {4}
rs_kind: ; {4}
        sty     okind ; {4}
        lda     RDOOR,x         ; the door of the room {4}
        and     opened ; {4}
        beq     rs_closed ; {4}
        lda     CM_LO,x         ; open (or no door)
        ldy     CM_HI,x
        bne     rs_map          ; (never 0) {4}
rs_closed: ; {4}
        lda     CMC_LO,x ; {4}
        ldy     CMC_HI,x ; {4}
rs_map: sta     cmap
        sty     cmap+1
        ldx     #5              ; VICTORY {6}
        lda     won ; {6}
        bne     rs_name ; {6}
        dex                     ; GAME OVER {6}
;|        ldx     #4              ; GAME OVER {5-5}
        lda     over ; {5}
        beq     rs_play ; {5}
rs_name: ; {5}
        jmp     name ; {5}
rs_play: ; {4}
        lda     txp ; {4}
        clc                     ; (no carry: one page) {4}
        adc     #40 ; {4}
        ldy     key ; {4}
        beq     rs_key ; {4}
        adc     #8 ; {4}
rs_key: sta     txp+10 ; {4}
        rts
;{}

; --------------------------------------------------------- {4}
; p1_bands: what player 1 shows. Band A (above the {5}
; seam, or the whole room): the thing of the room and the {5}
; guard of the band (the second guard with a seam, else {5}
; the first), each when it is there (the gate goes once {5}
; open, a guard once killed); both in turn: the thing in {5}
; even frames, the guard in odd ones (the flicker; they {5}
; share lines); neither: the empty figure. Band B: the {5}
; first guard, or the empty figure when it is dead (its {5}
; column, in the coarse delay and the fine move of the {5}
; seam, comes from things.asm, after it crawls). {5}
; A guard stunned by a first blow blinks. {9}
; In the throne room: p1_throne. {6}
;|; p1_bands: what player 1 shows: the thing of the room {4-4}
;|; (the gate goes once open), or the empty figure. {4-4}
; The pointers: base of the figure (two frames, every 16 {4}
; frames) + top line. {4}

p1_bands: ; {4}
        ldx     room ; {4}
        cpx     #THRONE_ROOM ; {6}
        bne     pb_room ; {6}
        jmp     p1_throne       ; the King or the crown {6}
pb_room: ; {6}
        lda     SEAM,x ; {5}
        sta     zcnt            ; the kernel counts it down {5}
        beq     pb_one          ; no seam: the first guard {5}
        txa ; {5}
        ora     #16             ; the second (entry 16 + r) {5}
        tax ; {5}
        lda     #2              ; its bit in SC_LIVE {5}
        ldy     #1              ; its place in the SC tables {5}
        bne     pb_guard ; {5}
pb_one: lda     #1 ; {5}
        ldy     #0 ; {5}
pb_guard: ; {5}
        and     SCR+SC_LIVE ; {5}
        beq     pb_noguard      ; dead {5}
        lda     S_TOP,x ; {5}
        beq     pb_noguard      ; none {5}
        lda     SCR+SC_GT,y     ; stunned, it blinks {9}
        beq     pb_seen ; {9}
        lda     frames ; {9}
        and     #FLASH_FRAMES ; {9}
        bne     pb_noguard ; {9}
pb_seen: ; {9}
        lda     S_TOP,x ; {9}
        sta     tmp             ; its top line {5}
        ldx     room ; {5}
        lda     okind ; {5}
        cmp     #NONE_KIND ; {5}
        beq     pb_show         ; no thing: the guard {5}
        lda     frames ; {5}
        lsr ; {5}
        bcs     pb_show         ; both: odd frames the guard {5}
        bcc     pb_thing ; {5}
pb_noguard: ; {5}
        ldx     room ; {5}
pb_thing: ; {4}
        lda     OB_TOP,x        ; the thing (or nothing) {4}
        sta     oy ; {4}
        lda     OB_X,x ; {4}
        sta     ox ; {4}
        lda     #8 ; {4}
        sta     odir ; {4}
        lda     okind ; {4}
        bpl     pb_ptrs         ; (always) {5}
pb_show: ; {5}
        lda     tmp             ; the guard {5}
        sta     oy ; {5}
        lda     SCR+SC_SX,y ; {5}
        sta     ox ; {5}
        lda     SCR+SC_SD,y ; {5}
        sta     odir ; {5}
        lda     S_KIND,x ; {5}
pb_ptrs: ; {4}
        jsr     frame_of ; {4}
        lda     OG_LO,y ; {4}
        clc ; {4}
        adc     oy ; {4}
        sta     sgfx ; {4}
        lda     OG_HI,y ; {4}
        adc     #0 ; {4}
        sta     sgfx+1 ; {4}
        lda     OC_LO,y ; {4}
        clc ; {4}
        adc     oy ; {4}
        sta     scol ; {4}
        lda     OC_HI,y ; {4}
        adc     #0 ; {4}
        sta     scol+1 ; {4}
        lda     zcnt            ; band B: the first guard {5}
        beq     pb_done ; {5}
        lda     #1 ; {5}
        and     SCR+SC_LIVE ; {5}
        beq     pb_dead ; {5}
        lda     SCR+SC_GT       ; stunned, it blinks {9}
        beq     pb_live ; {9}
        lda     frames ; {9}
        and     #FLASH_FRAMES ; {9}
        bne     pb_dead ; {9}
pb_live: ; {9}
        lda     S_KIND,x ; {5}
        bne     pb_fig          ; (never 0: a serpent) {5}
pb_dead: ; {5}
        lda     #NONE_KIND ; {5}
pb_fig: jsr     frame_of ; {5}
        lda     OG_LO,y ; {5}
        clc ; {5}
        adc     S_TOP,x ; {5}
        sta     s2gfx ; {5}
        lda     OG_HI,y ; {5}
        adc     #0 ; {5}
        sta     s2gfx+1 ; {5}
        lda     OC_LO,y ; {5}
        clc ; {5}
        adc     S_TOP,x ; {5}
        sta     s2col ; {5}
        lda     OC_HI,y ; {5}
        adc     #0 ; {5}
        sta     s2col+1 ; {5}
        lda     SCR+SC_SD ; {5}
        sta     zref            ; (its column: zcoarse, {5}
pb_done:                        ; SC_HM: things.asm) {5}
        rts ; {4}

; p1_throne: player 1 in the throne room (no seam): {6}
; the King, twice as wide, at his column and top line, {6}
; facing Sir Roderick, his two frames in turn; his colours {6}
; (TC): plain, spitting (the venom flies: bit 1 on his mouth {6}
; only), flashing after a blow (every other FLASH_FRAMES {6}
; frames), or both. Or the crown four times as wide on the {6}
; throne, or its pieces. The pointers: base + top line. {6}

p1_throne: ; {6}
        lda     #0 ; {6}
        sta     zcnt            ; no seam {6}
        lda     SCR+SC_CROWN ; {6}
        beq     pt_king ; {6}
        tay                     ; 1 the crown, 2 its pieces {6}
        iny                     ; TG: 2, 3; TC: 4, 5 {6}
        lda     #NUS_CROWN ; {6}
        sta     onus ; {6}
        lda     #CROWN_X ; {6}
        sta     ox ; {6}
        lda     #CROWN_TOP ; {6}
        sta     oy ; {6}
        lda     #0 ; {6}
        sta     odir ; {6}
        tya ; {6}
        clc ; {6}
        adc     #2 ; {6}
        tax                     ; its colours {6}
        bne     pt_ptrs         ; (always) {6}
pt_king: ; {6}
        lda     #NUS_KING ; {6}
        sta     onus ; {6}
        lda     #KING_X ; {6}
        sta     ox ; {6}
        lda     SCR+SC_KT ; {6}
        sta     oy ; {6}
        ldx     #8              ; facing Sir Roderick {6}
        lda     kx ; {6}
        cmp     #SPIT_LEFT ; {6}
        bcc     pt_dir ; {6}
        ldx     #0 ; {6}
pt_dir: stx     odir ; {6}
        ldx     #0              ; his colours: plain, {6}
        lda     SCR+SC_VD ; {6}
        beq     pt_flash ; {6}
        inx                     ; spitting {6}
pt_flash: ; {6}
        lda     SCR+SC_KF ; {6}
        beq     pt_frame ; {6}
        lda     frames ; {6}
        and     #FLASH_FRAMES ; {6}
        beq     pt_frame ; {6}
        inx                     ; flashing (+ 2) {6}
        inx ; {6}
pt_frame: ; {6}
        lda     #0 ; {6}
        jsr     frame_of        ; Y: his frame, 0 or 1 {6}
pt_ptrs:                        ; Y: the figure, X: colours {6}
        lda     TG_LO,y ; {6}
        clc ; {6}
        adc     oy ; {6}
        sta     sgfx ; {6}
        lda     TG_HI,y ; {6}
        adc     #0 ; {6}
        sta     sgfx+1 ; {6}
        lda     TC_LO,x ; {6}
        clc ; {6}
        adc     oy ; {6}
        sta     scol ; {6}
        lda     TC_HI,x ; {6}
        adc     #0 ; {6}
        sta     scol+1 ; {6}
        rts ; {6}

; frame_of: Y = A + the frame of the figure (its two {4}
; frames take turns every 16 frames) {4}
frame_of: ; {4}
        sta     tmp+1 ; {4}
        lda     frames ; {4}
        lsr ; {4}
        lsr ; {4}
        lsr ; {4}
        lsr ; {4}
        and     #1 ; {4}
        clc ; {4}
        adc     tmp+1 ; {4}
        tay ; {4}
        rts ; {4}

; ---------------------------------------------------------
; prep_room: the pointers of Sir Roderick and of the
; colours of the room, the torches, the energy bar; the {3}
; blade; the positions of the six digits of the HUD, of {3}
; the blade, of the ball, of the venom {6}
;|; the blade, of the ball {3-5}
;|; colours of the room; the blade and its position {2-2}
;|; colours of the room {1-1}

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
        lda     hurt            ; wounded, the colours {5}
        beq     pr_kc           ; of the flash every other {5}
        lda     frames          ; FLASH_FRAMES frames (not {5}
        and     #FLASH_FRAMES   ; in the thrust: they switch {5}
        beq     pr_kc           ; the blade) {5}
        cpy     #THRUST_POSE ; {5}
        beq     pr_kc ; {5}
        ldy     #FLASH_KC ; {5}
pr_kc:  lda     KC_LO,y
        clc
        adc     ky
        sta     kcol
        lda     KC_HI,y
        adc     #0
        sta     kcol+1
        ; colours of the room: its scheme gives COLUBK (the {3}
        ; water changes it) and COLUPF {3}
;|        ; colours of the room: its scheme gives COLUBK and {1-2}
;|        ; COLUPF {1-2}
        ldx     room
        ldy     SCHEME,x
        lda     frames ; {3}
        and     #8 ; {3}
        beq     pr_col0 ; {3}
        lda     CB1_LO,y ; {3}
        sta     cbk ; {3}
        lda     CB1_HI,y ; {3}
        bne     pr_col          ; (never 0) {3}
pr_col0: ; {3}
        lda     CB0_LO,y
        sta     cbk
        lda     CB0_HI,y
pr_col: sta     cbk+1
        lda     CP_LO,y
        sta     cpf
        lda     CP_HI,y
        sta     cpf+1
        ; torches: course 0 changes every four frames {3}
        lda     RF_HI,x ; {3}
        beq     pr_digits ; {3}
        sta     tmp+1 ; {3}
        lda     RF_LO,x ; {3}
        sta     tmp ; {3}
        ldy     #3              ; bit 2 of frames clear: the {3}
        lda     frames          ; flame stays in its niche {3}
        and     #4 ; {3}
        beq     pr_t0 ; {3}
        ldy     #0              ; bit 2 set: it rises {3}
pr_t0: ; {3}
        lda     (tmp),y ; {3}
        sta     SCW+SC_PF0+19 ; {3}
        iny ; {3}
        lda     (tmp),y ; {3}
        sta     SCW+SC_PF1+19 ; {3}
        iny ; {3}
        lda     (tmp),y ; {3}
        sta     SCW+SC_PF2+19 ; {3}
pr_digits: ; {3}
        ; (the digits are pointed to in the overscan, {3}
        ; after the points: digits) {3}
        ; energy bar {3}
        ldx     energy ; {3}
        lda     BAR_PF1,x ; {3}
        sta     bar1 ; {3}
        lda     BAR_PF2,x ; {3}
        sta     bar2 ; {3}
        jsr     blade           ; knight.asm {2}
        ; positions: the six digits with players 0 and 1, 8 {3}
        ; pixels apart, three copies each, both delayed; the {3}
        ; blade with missile 0 (RESMP0 first: while it is 2 {3}
        ; the missile stays on player 0); the ball where the {3}
        ; room has its plug (in any room: it shows only when {3}
        ; ENABL is on) {3}
;|        ; the position of the blade, missile 0 (RESMP0 {2-2}
;|        ; first: while it is 2 the missile stays on player {2-2}
;|        ; 0; the HMOVE of HUD line 28 moves it with Sir {2-2}
;|        ; Roderick) {2-2}
        lda     swres ; {2}
        sta     RESMP0 ; {2}
        lda     #SCORE_X ; {3}
        ldx     #0 ; {3}
        jsr     place ; {3}
        lda     #SCORE_X+8 ; {3}
        ldx     #1 ; {3}
        jsr     place ; {3}
        lda     swx ; {2}
        ldx     #2 ; {2}
        jsr     place ; {2}
        ldx     room ; {3}
        lda     BALL_X,x ; {3}
        ldx     #4 ; {3}
        jsr     place ; {3}
        ; the venom, missile 1, only in the throne room {6}
        ; while it flies (RESMP1 0: shown, at the column {6}
        ; that puts its first pixel at SC_VP); otherwise {6}
        ; RESMP1 2 keeps it on player 1, hidden {6}
        lda     #2 ; {6}
        sta     RESMP1 ; {6}
        lda     room ; {6}
        cmp     #THRONE_ROOM ; {6}
        bne     pr_hmove ; {6}
        lda     SCR+SC_VD ; {6}
        beq     pr_hmove ; {6}
        lda     #0 ; {6}
        sta     RESMP1 ; {6}
        lda     SCR+SC_VP ; {6}
        sec ; {6}
        sbc     #M_OFFSET ; {6}
        bcs     pr_vcol ; {6}
        adc     #160            ; (round the screen) {6}
pr_vcol: ; {6}
        ldx     #3 ; {6}
        jsr     place ; {6}
pr_hmove:
        sta     WSYNC ; {3}
        sta     HMOVE           ;  2 {3}
        lda     #3 ; {3}
        sta     NUSIZ0 ; {3}
        sta     NUSIZ1 ; {3}
        lda     #1 ; {3}
        sta     VDELP0 ; {3}
        sta     VDELP1 ; {3}
        lda     #$31            ; reflected playfield, the
        sta     CTRLPF          ; ball 8 pixels wide
        lda     #0 ; {3}
        sta     REFP0 ; {3}
        sta     REFP1 ; {3}
        sta     HMCLR           ; 34: 32 cycles after HMOVE {3}
        rts

; digits: the six pointers of the score in the HUD, digit d {3}
; at DIGITS + 8 d (in the overscan of a game, after the {3}
; things that add points, and in new_game; not in the {3}
; VBLANK, which is short when a room changes) {3}
digits: ldx     #0 ; {3}
        ldy     #0 ; {3}
di_one: lda     score,x ; {3}
        lsr ; {3}
        lsr ; {3}
        lsr ; {3}
        lsr ; {3}
        jsr     dig_ptr ; {3}
        lda     score,x ; {3}
        and     #$0F ; {3}
        jsr     dig_ptr ; {3}
        inx ; {3}
        cpx     #3 ; {3}
        bne     di_one ; {3}
        rts ; {3}

; dig_ptr: A = digit; pointer Y in dig (Y += 2) {3}
dig_ptr: ; {3}
        asl ; {3}
        asl ; {3}
        asl ; {3}
        clc ; {3}
        adc     #<DIGITS ; {3}
        sta     dig,y ; {3}
        lda     #>DIGITS ; {3}
        adc     #0 ; {3}
        sta     dig+1,y ; {3}
        iny ; {3}
        iny ; {3}
        rts ; {3}

; place: object X (0 player 0, 1 player 1, 2 missile 0, 3 {2}
; missile 1, 4 the ball) at column A: the first pixel of a {2}
; player is A + 3, of a missile or the ball A + 2. Takes one {2}
; line: the WSYNC, then 15 pixels per 5 cycles. {2}
; (its loop in one page: a branch that crosses one takes a {2}
; cycle more, and the column would be wrong; the padding {2}
; comes after an rts) {2}
        IF (* & $FF00) != ((*+8) & $FF00) ; {2}
        ALIGN   256 ; {2}
        ENDIF ; {2}
place: ; {2}
        sta     WSYNC ; {2}
        sec ; {2}
pl_div: sbc     #15 ; {2}
        bcs     pl_div          ; (pl_div) {2}
        eor     #7 ; {2}
        asl ; {2}
        asl ; {2}
        asl ; {2}
        asl ; {2}
        sta     HMP0,x ; {2}
        sta     RESP0,x ; {2}
        rts ; {2}
