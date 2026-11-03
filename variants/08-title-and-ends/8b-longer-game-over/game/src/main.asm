; main.asm - bank 7: start, the frame, and what is done
; in it besides the kernels:
; - the title, SELECT, the end screens (bank 6) and their
;   songs;
; - the buttons: RESET starts again;
; - GAME OVER, VICTORY;
; - setting a room up: its playfield comes from bank 3
;   into the Superchip RAM;
; - what the kernels need: Sir Roderick, the colours of
;   the room, the HUD, the bands of player 1, the King or
;   the crown on player 1, the venom on missile 1.
; In the overscan the things of the room, the guards and
; the Serpent King (bank 4, in a game) and the sound
; player (bank 5).

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
        jmp     main

kernel_done:                    ; back from a kernel (the
                                ; overscan timer is running)
        lda     screen          ; the title, an end screen:
        beq     kd_sound        ; only the sound
        jsr     TO_THINGS       ; the things (bank 4)
        jsr     digits          ; the score's digits
kd_sound:                       ; the sound (bank 5)
        jsr     TO_SOUND
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
        lda     screen
        bne     fr_game
        lda     over            ; screen 0 and over
        ora     won             ; or won: an end screen
        bne     fr_ends
        lda     pressed         ; the title: SELECT chooses
        and     #$02            ; the next sound mode
        beq     fr_start
        ldx     mode
        inx
        cpx     #3
        bcc     fr_mode
        ldx     #0
fr_mode:
        stx     mode
fr_start:
        lda     pressed         ; the button or RESET starts
        and     #$81            ; a game
        bne     fr_new
        jmp     fr_title
fr_new: jsr     new_game
        jmp     fr_room
fr_game:
        lda     pressed
        lsr                     ; bit 0: RESET
        bcc     fr_play
        jsr     new_game        ; start again
        jmp     fr_room
fr_play:
        lda     won             ; VICTORY: nothing moves
        beq     fr_over
        cmp     #VIC_FRAMES     ; for VIC_FRAMES, then the
        bcs     fr_end          ; end screen
        inc     won
        bne     fr_room         ; (never 0)
fr_over:
        lda     over            ; GAME OVER: the same,
        beq     fr_knight
        cmp     #GO_FRAMES      ; for GO_FRAMES
        bcs     fr_end
        inc     over
        bne     fr_room         ; (never 0)
fr_end: lda     #0              ; the end screen: screen 0,
        sta     screen          ; over or won go on counting
fr_ends:
        lda     pressed         ; RESET: a game at once
        lsr
        bcc     fe_count
        jsr     new_game
        jmp     fr_room
fe_count:
        lda     won             ; END_FRAMES more, then the
        beq     fe_over         ; button
        cmp     #VIC_FRAMES+END_FRAMES
        bcs     fe_button
        inc     won
        bne     fe_draw         ; (never 0)
fe_over:
        lda     over
        cmp     #GO_FRAMES+END_FRAMES
        bcs     fe_button
        inc     over
        bne     fe_draw         ; (never 0)
fe_button:
        bit     pressed         ; the button: the title, the
        bpl     fe_draw         ; theme from its start
        lda     #0
        sta     over
        sta     won
        jsr     theme
        jmp     fr_title
fe_draw:
        jsr     end_score       ; the digits for the screen
        lda     #$FF
        sta     shown           ; set the room up again
fe_wait:                        ; the tests read INTIM here
        lda     INTIM
        bne     fe_wait
        sta     WSYNC
        jmp     TO_ENDS         ; bank 6
fr_knight:
        jsr     knight          ; Sir Roderick (knight.asm)
fr_room:
        jsr     setup_room
        jsr     room_state
        jsr     p1_bands
        jsr     prep_room
vb_end:                         ; the tests read INTIM here
        lda     INTIM
        bne     vb_end
        sta     WSYNC
        jmp     hud             ; HUD (hud.asm), then room

fr_title:
        lda     #$FF
        sta     shown           ; set the room up again
vb_wait:
        lda     INTIM
        bne     vb_wait
        sta     WSYNC
        jmp     TO_TITLE

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
; theme: the theme from its first step; the player
; silences what was playing (a new song: smode $FF)

theme:  lda     #SONG_THEME
        sta     song
        lda     #$FF
        sta     smode
        rts

; end_score: the six digits of the score into the
; Superchip RAM for the end screen (bank 6): column k at
; 9 k, bottom first as the tables of a block: byte 0 empty,
; bytes 1-8 the digit (DIGITS is bottom first too)

end_score:
        ldx     #0              ; X: the column's byte
        stx     tmp+1           ; the digit, 0-5
es_dig: lda     tmp+1
        lsr                     ; C: an odd digit
        tay
        lda     score,y
        bcs     es_lo           ; odd: the low nibble
        lsr
        lsr
        lsr
        lsr
es_lo:  and     #$0F
        asl
        asl
        asl
        tay                     ; 8 x the digit
        lda     #0
        sta     SCW,x           ; the empty line
        lda     #8
        sta     tmp
es_byte:
        inx
        lda     DIGITS,y
        sta     SCW,x
        iny
        dec     tmp
        bne     es_byte
        inx                     ; the next column
        inc     tmp+1
        lda     tmp+1
        cmp     #6
        bne     es_dig
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
        sta     key             ; no key, all closed
        sta     opened
        sta     hurt            ; not hurt, playing
        sta     over
        sta     won             ; not won, no parry, the
        sta     parry           ; King on his throne
        sta     SCW+SC_CROWN
        lda     #ENERGY_FULL
        sta     energy
        lda     #$FF
        sta     shown           ; the room is set up again
        jsr     theme           ; the theme anew
        jmp     digits          ; (score 0)

; ---------------------------------------------------------
; setup_room: when the screen changes, the playfield of
; the room goes into the Superchip RAM (bank 3)
; - with its door open if it is;
; - the HUD gets the name of its level; the plug of the
;   room is chosen;
; - the plates of the spikes start down, NUSIZ1 of the
;   room;
; - the guards go to their start alive (the army is
;   infinite);
; - in the throne room the King starts again (in front
;   of his throne, no blow, no venom; unless he has been
;   beaten: the crown stays)

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
        lda     SU_DOWN,x       ; the plates: down, for the
        sta     spk             ; time of the level
        lda     #0
        sta     spup
        sta     SCW+SC_ACC      ; the guards: no fraction,
        lda     #3              ; both alive,
        sta     SCW+SC_LIVE
        lda     #8              ; facing left,
        sta     SCW+SC_SD
        sta     SCW+SC_SD+1
        ldx     room
        lda     S_X,x           ; at their start (the first:
        sta     SCW+SC_SX       ; its coarse column and fine
        lda     S_X+16,x        ; move for the seam, as
        sta     SCW+SC_SX+1     ; things.asm keeps them)
        lda     S_CO,x
        sta     zcoarse
        lda     S_HM,x
        sta     SCW+SC_HM
        cpx     #THRONE_ROOM
        bne     su_plug
        lda     #KING_START     ; the King
        sta     SCW+SC_KT
        lda     #0
        sta     SCW+SC_KH
        sta     SCW+SC_KF
        sta     SCW+SC_VD
        sta     SCW+SC_VA
        lda     #SPIT_FIRST
        sta     SCW+SC_KS
su_plug:
        lda     PLUG,x          ; the ball on or off
        sta     plug
        lda     OB_NUS,x
        sta     onus
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
; the things of the room (things.asm, bank 4, in the
; overscan): the thing of player 1 closed or open, the
; collision map with the door closed or open, the HUD
; with the key after LEVEL n (the sixth column of the
; name, 8 bytes on) or, after the end, GAME OVER or
; VICTORY

room_state:
        ldx     room
        ldy     OB_KIND0,x      ; the thing: closed
        lda     OB_BIT,x
        and     opened
        beq     rs_kind
        ldy     OB_KIND1,x      ; open
rs_kind:
        sty     okind
        lda     RDOOR,x         ; the door of the room
        and     opened
        beq     rs_closed
        lda     CM_LO,x         ; open (or no door)
        ldy     CM_HI,x
        bne     rs_map          ; (never 0)
rs_closed:
        lda     CMC_LO,x
        ldy     CMC_HI,x
rs_map: sta     cmap
        sty     cmap+1
        ldx     #5              ; VICTORY
        lda     won
        bne     rs_name
        dex                     ; GAME OVER
        lda     over
        beq     rs_play
rs_name:
        jmp     name
rs_play:
        lda     txp
        clc                     ; (no carry: one page)
        adc     #40
        ldy     key
        beq     rs_key
        adc     #8
rs_key: sta     txp+10
        rts

; ---------------------------------------------------------
; p1_bands: what player 1 shows. Band A (above the
; seam, or the whole room): the thing of the room and the
; guard of the band (the second guard with a seam, else
; the first), each when it is there (the gate goes once
; open, a guard once killed); both in turn: the thing in
; even frames, the guard in odd ones (the flicker; they
; share lines); neither: the empty figure. Band B: the
; first guard, or the empty figure when it is dead (its
; column, in the coarse delay and the fine move of the
; seam, comes from things.asm, after it crawls).
; In the throne room: p1_throne.
; The pointers: base of the figure (two frames, every 16
; frames) + top line.

p1_bands:
        ldx     room
        cpx     #THRONE_ROOM
        bne     pb_room
        jmp     p1_throne       ; the King or the crown
pb_room:
        lda     SEAM,x
        sta     zcnt            ; the kernel counts it down
        beq     pb_one          ; no seam: the first guard
        txa
        ora     #16             ; the second (entry 16 + r)
        tax
        lda     #2              ; its bit in SC_LIVE
        ldy     #1              ; its place in the SC tables
        bne     pb_guard
pb_one: lda     #1
        ldy     #0
pb_guard:
        and     SCR+SC_LIVE
        beq     pb_noguard      ; dead
        lda     S_TOP,x
        beq     pb_noguard      ; none
        sta     tmp             ; its top line
        ldx     room
        lda     okind
        cmp     #NONE_KIND
        beq     pb_show         ; no thing: the guard
        lda     frames
        lsr
        bcs     pb_show         ; both: odd frames the guard
        bcc     pb_thing
pb_noguard:
        ldx     room
pb_thing:
        lda     OB_TOP,x        ; the thing (or nothing)
        sta     oy
        lda     OB_X,x
        sta     ox
        lda     #8
        sta     odir
        lda     okind
        bpl     pb_ptrs         ; (always)
pb_show:
        lda     tmp             ; the guard
        sta     oy
        lda     SCR+SC_SX,y
        sta     ox
        lda     SCR+SC_SD,y
        sta     odir
        lda     S_KIND,x
pb_ptrs:
        jsr     frame_of
        lda     OG_LO,y
        clc
        adc     oy
        sta     sgfx
        lda     OG_HI,y
        adc     #0
        sta     sgfx+1
        lda     OC_LO,y
        clc
        adc     oy
        sta     scol
        lda     OC_HI,y
        adc     #0
        sta     scol+1
        lda     zcnt            ; band B: the first guard
        beq     pb_done
        lda     #1
        and     SCR+SC_LIVE
        beq     pb_dead
        lda     S_KIND,x
        bne     pb_fig          ; (never 0: a serpent)
pb_dead:
        lda     #NONE_KIND
pb_fig: jsr     frame_of
        lda     OG_LO,y
        clc
        adc     S_TOP,x
        sta     s2gfx
        lda     OG_HI,y
        adc     #0
        sta     s2gfx+1
        lda     OC_LO,y
        clc
        adc     S_TOP,x
        sta     s2col
        lda     OC_HI,y
        adc     #0
        sta     s2col+1
        lda     SCR+SC_SD
        sta     zref            ; (its column: zcoarse,
pb_done:                        ; SC_HM: things.asm)
        rts

; p1_throne: player 1 in the throne room (no seam):
; the King, twice as wide, at his column and top line,
; facing Sir Roderick, his two frames in turn; his colours
; (TC): plain, spitting (the venom flies: bit 1 on his mouth
; only), flashing after a blow (every other FLASH_FRAMES
; frames), or both. Or the crown four times as wide on the
; throne, or its pieces. The pointers: base + top line.

p1_throne:
        lda     #0
        sta     zcnt            ; no seam
        lda     SCR+SC_CROWN
        beq     pt_king
        tay                     ; 1 the crown, 2 its pieces
        iny                     ; TG: 2, 3; TC: 4, 5
        lda     #NUS_CROWN
        sta     onus
        lda     #CROWN_X
        sta     ox
        lda     #CROWN_TOP
        sta     oy
        lda     #0
        sta     odir
        tya
        clc
        adc     #2
        tax                     ; its colours
        bne     pt_ptrs         ; (always)
pt_king:
        lda     #NUS_KING
        sta     onus
        lda     #KING_X
        sta     ox
        lda     SCR+SC_KT
        sta     oy
        ldx     #8              ; facing Sir Roderick
        lda     kx
        cmp     #SPIT_LEFT
        bcc     pt_dir
        ldx     #0
pt_dir: stx     odir
        ldx     #0              ; his colours: plain,
        lda     SCR+SC_VD
        beq     pt_flash
        inx                     ; spitting
pt_flash:
        lda     SCR+SC_KF
        beq     pt_frame
        lda     frames
        and     #FLASH_FRAMES
        beq     pt_frame
        inx                     ; flashing (+ 2)
        inx
pt_frame:
        lda     #0
        jsr     frame_of        ; Y: his frame, 0 or 1
pt_ptrs:                        ; Y: the figure, X: colours
        lda     TG_LO,y
        clc
        adc     oy
        sta     sgfx
        lda     TG_HI,y
        adc     #0
        sta     sgfx+1
        lda     TC_LO,x
        clc
        adc     oy
        sta     scol
        lda     TC_HI,x
        adc     #0
        sta     scol+1
        rts

; frame_of: Y = A + the frame of the figure (its two
; frames take turns every 16 frames)
frame_of:
        sta     tmp+1
        lda     frames
        lsr
        lsr
        lsr
        lsr
        and     #1
        clc
        adc     tmp+1
        tay
        rts

; ---------------------------------------------------------
; prep_room: the pointers of Sir Roderick and of the
; colours of the room, the torches, the energy bar; the
; blade; the positions of the six digits of the HUD, of
; the blade, of the ball, of the venom

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
        lda     hurt            ; wounded, the colours
        beq     pr_kc           ; of the flash every other
        lda     frames          ; FLASH_FRAMES frames (not
        and     #FLASH_FRAMES   ; in the thrust: they switch
        beq     pr_kc           ; the blade)
        cpy     #THRUST_POSE
        beq     pr_kc
        ldy     #FLASH_KC
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
        ; the venom, missile 1, only in the throne room
        ; while it flies (RESMP1 0: shown, at the column
        ; that puts its first pixel at SC_VP); otherwise
        ; RESMP1 2 keeps it on player 1, hidden
        lda     #2
        sta     RESMP1
        lda     room
        cmp     #THRONE_ROOM
        bne     pr_hmove
        lda     SCR+SC_VD
        beq     pr_hmove
        lda     #0
        sta     RESMP1
        lda     SCR+SC_VP
        sec
        sbc     #M_OFFSET
        bcs     pr_vcol
        adc     #160            ; (round the screen)
pr_vcol:
        ldx     #3
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
