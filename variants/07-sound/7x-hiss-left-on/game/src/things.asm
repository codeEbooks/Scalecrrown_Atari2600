; things.asm - bank 4: the things of the rooms, the guards
; and the Serpent King
;
; Called once a frame in the overscan of a game, from bank 7
; through the trampoline TO_THINGS, before the sound: what
; Sir Roderick's move of this frame did, after the picture
; that showed it.
; - The spikes: the time of the plates. setup_room
;   (main.asm) starts them down when he comes into a room;
;   when they turn, their version of the two courses goes
;   into the Superchip RAM, where the kernel draws the room
;   from.
; - The hurt: on a raised plate he loses SPIKE_DAMAGE units
;   of energy, again every HURT_FRAMES while he stays on
;   it. While the count of a wound goes down (after the
;   spikes or a bite) nothing hurts him, and he flashes.
; - The guards, each one alive: the blade of a thrust
;   kills a serpent it touches (SERPENT_BCD points);
;   a serpent whose box touches his bites (BITE_DAMAGE,
;   then BITE_FRAMES without wounds); then they crawl
;   along their paths, turning at the ends, at the speed of
;   the room (a fraction of a pixel a frame).
;   The column of the first guard, for the seam of the
;   next frame (zcoarse, SC_HM).
; - The thing of the room: a chest he touches opens and
;   gives him the key of the level; a door he stands in
;   front of with that key opens (the key is used up), and
;   the open version of the grate goes into the Superchip
;   RAM. Points for both, and their sound in the SOUND FX
;   mode.
; - The throne room, in place of the guards: the Serpent
;   King (throne, below) or the crown.
; - GAME OVER: energy 0. From then on nothing here; nor
;   after VICTORY.
; What player 1 shows, the collision map and the key in the
; HUD follow in the next frame (room_state, p1_bands in
; main.asm).
;
; The tables (bank4.asm, from dungeon.py and rules.py): for
; each room its lists of versions, the bit of its thing in
; `opened`, where he touches it, where the plates are;
; its guards (32 entries: r the first, 16 + r the second).

        IF CHEST_BCD == 0 || SPK_UP == 0
        ERR                     ; (the branches below)
        ENDIF

things:
        lda     over            ; GAME OVER, VICTORY: all
        ora     won             ; stops
        beq     th_go
        rts
th_go:
        ; --- the plates: down for the time of the level, up
        ; for SPK_UP frames
        dec     spk
        bne     th_hurt
        ldy     room
        lda     spup            ; they turn
        eor     #1
        sta     spup
        beq     th_down
        lda     #SPK_UP
        sta     spk
        ldx     SPU4,y          ; the raised version
        bne     th_turn         ; (an empty list is entry 0:
        beq     th_hurt         ; nothing to write)
th_down:
        tya
        lsr
        lsr
        tax                     ; level - 1
        lda     TH_DOWN,x
        sta     spk
        ldx     SPD4,y          ; the lowered version
th_turn:
        jsr     put
        ; --- the hurt: while it counts down, no new one
th_hurt:
        lda     hurt
        beq     th_feet
        dec     hurt
        bne     th_guards
th_feet:
        lda     spup
        beq     th_guards       ; the plates are down
        lda     ky
        cmp     #PLATE_Y0
        bcc     th_guards
        cmp     #PLATE_Y1
        bcs     th_guards       ; his feet off their lines
        ldx     room
        lda     kx              ; the middle of his feet
        cmp     PXA0,x          ; over the first plate
        bcc     th_plb
        cmp     PXA1,x
        bcc     th_hit
th_plb: cmp     PXB0,x          ; or over the second
        bcc     th_guards
        cmp     PXB1,x
        bcs     th_guards
th_hit: lda     #SPIKE_DAMAGE   ; a wound (the routine of
        jsr     wound           ; every wound), with the
        lda     #HURT_FRAMES    ; rest of the spikes
        sta     hurt
        lda     #SFX_HURT
        sta     sfxreq
        ; --- the guards, the King
th_guards:
        ldx     room
        cpx     #THRONE_ROOM
        bne     th_serp
        jsr     throne
        jmp     th_thing
th_serp:
        jsr     guards
        ; --- the thing of the room, if he touches it
th_thing:
        ldx     room
        lda     TBIT,x
        beq     th_done         ; nothing here
        and     opened
        bne     th_done         ; open already
        lda     kx
        cmp     TX0,x
        bcc     th_done
        cmp     TX1,x
        bcs     th_done
        lda     ky
        cmp     TY0,x
        bcc     th_done
        cmp     TY1,x
        bcs     th_done
        lda     room            ; he touches it
        lsr
        lsr
        tay
        iny                     ; Y: the level, 1-4
        lda     TBIT,x
        cmp     #$10
        bcs     th_door
        ora     opened          ; a chest: it opens, he has
        sta     opened          ; the key of the level
        sty     key
        lda     #SFX_CHEST
        sta     sfxreq
        lda     #CHEST_BCD
        bne     th_points
th_door:
        cpy     key             ; a door: only with the key
        bne     th_done         ; of its level
        ora     opened
        sta     opened
        lda     #0
        sta     key             ; the key is used up
        lda     #SFX_DOOR
        sta     sfxreq
        lda     DOP4,x          ; the grate opens (the gate:
        tax                     ; an empty list)
        jsr     put
        lda     #DOOR_BCD
th_points:
        jsr     points
        ; --- GAME OVER: energy 0
th_done:
        lda     energy
        bne     th_end
        lda     #1
        sta     over
        lda     #0              ; he stands, no flash
        sta     hurt
        sta     kpose
        sta     thrust
        sta     parry           ; no parry, the venom is
        sta     SCW+SC_VD       ; gone
        lda     #SFX_GAMEOVER
        sta     sfxreq
th_end: rts

; points: A (BCD, hundreds) added to the score. The score
; is BCD; the points go to its middle byte, the carry to
; the first.
points: sed
        clc
        adc     score+1
        sta     score+1
        lda     score
        adc     #0
        sta     score
        cld
        rts

; put: a version into the Superchip RAM: the entries of the
; lists VI4 (index) and VV4 (value) from entry X up to the
; index $FF
put:    ldy     VI4,x
        bmi     pu_done
        lda     VV4,x
        sta     SCW,y
        inx
        bne     put
pu_done:
        rts

; ---------------------------------------------------------
; guards: the guards of the room one after the other, each
; with X its entry in the tables (r, then 16 + r) and Y its
; place in the Superchip (0, 1); all serpents. tmp+1: bit
; 0, they crawl a pixel in this frame (the fraction of the
; room's speed carries).

guards: ldx     room
        lda     SCR+SC_ACC
        clc
        adc     CRAWL,x
        sta     SCW+SC_ACC
        lda     #0
        rol
        sta     tmp+1
        ldy     #0              ; the first guard
gu_one: lda     GBIT,y
        and     SCR+SC_LIVE
        beq     gu_next         ; dead
        lda     S_TOP4,x
        beq     gu_next         ; none
        jsr     guard
gu_next:
        txa
        ora     #16             ; the second
        tax
        iny
        cpy     #2
        bcc     gu_one
        ; the column of the first guard for the seam of
        ; the next frame: the delay (5 cycles a count) and
        ; the fine move, as place does it for the column - 3
        ; (the RESP1 of the seam writes a cycle after
        ; place's: 3 pixels more; a guard below a seam is
        ; never left of column 3)
        lda     SCR+SC_SX
        sec
        sbc     #3
        ldy     #0
gu_div: iny
        sbc     #15
        bcs     gu_div
        eor     #7
        asl
        asl
        asl
        asl
        sta     SCW+SC_HM
        sty     zcoarse
        rts

GBIT    .byte   1, 2            ; their bits in SC_LIVE

; guard: one guard alive, X its entry, Y its place
guard:
        ; - the blade: in a thrust (shown: swres 0), on the
        ; lines ky + BLADE_LINE and the one after, 1 to 15
        ; columns from him on the side he faces (with the
        ; guards 16 columns from the edges this is where the
        ; 8 pixels of the blade touch the guard's 8)
        lda     swres
        bne     ga_bite
        lda     ky
        clc
        adc     #BLADE_LINE+1
        sec
        sbc     S_TOP4,x
        cmp     #SERPENT_H+1    ; its lines and the guard's
        bcs     ga_bite         ; meet: 0-16
        lda     kdir
        bne     ga_left
        lda     SCR+SC_SX,y     ; facing right: the guard's
        sec                     ; column - his
        sbc     kx
        bcs     ga_dist         ; (below: the guard is left
        bcc     ga_bite         ; of him)
ga_left:
        lda     kx              ; facing left: his - the
        sec                     ; guard's
        sbc     SCR+SC_SX,y
        bcc     ga_bite
ga_dist:
        sbc     #1              ; (carry is set)
        cmp     #15
        bcs     ga_bite         ; not 1-15 columns
        lda     GBIT,y          ; killed
        eor     #$FF
        and     SCR+SC_LIVE
        sta     SCW+SC_LIVE
        lda     #SFX_KILL
        sta     sfxreq
        lda     #SERPENT_BCD
        jmp     points
        ; - the bite: their boxes meet (8 x 24, 8 x 16), and
        ; no wound is counting down
ga_bite:
        lda     hurt
        bne     ga_crawl
        lda     ky              ; lines: ky + 23 - top from
        clc                     ; 0 to 38
        adc     #KNIGHT_H-1
        sec
        sbc     S_TOP4,x
        cmp     #KNIGHT_H+SERPENT_H-1
        bcs     ga_crawl
        lda     kx              ; columns: kx - column + 7
        sec                     ; from 0 to 14
        sbc     SCR+SC_SX,y
        clc
        adc     #KNIGHT_W-1
        cmp     #2*KNIGHT_W-1
        bcs     ga_crawl
        lda     #BITE_DAMAGE    ; bitten
        jsr     wound
        lda     #SFX_BITE
        sta     sfxreq
        ; - the crawl: a pixel when the fraction carries
ga_crawl:
        lda     tmp+1
        lsr
        bcc     ga_done         ; no pixel in this frame
        ; - the way back and forth; at the end of its path
        ; it turns
ga_way: lda     SCR+SC_SD,y
        bne     ga_cl
        lda     SCR+SC_SX,y     ; to the right
        cmp     S_MAX4,x
        bcs     ga_tl           ; at the end: it turns
        adc     #1              ; (carry is clear)
        sta     SCW+SC_SX,y
        cmp     S_MAX4,x
        bne     ga_done
ga_tl:  lda     #8              ; it turns
        sta     SCW+SC_SD,y
        rts
ga_cl:  lda     SCR+SC_SX,y     ; to the left
        cmp     S_MIN4,x
        beq     ga_tr           ; at the end: it turns
        sbc     #1              ; (carry is set)
        sta     SCW+SC_SX,y
        cmp     S_MIN4,x
        bne     ga_done
ga_tr:  lda     #0
        sta     SCW+SC_SD,y
ga_done:
        rts

; ---------------------------------------------------------
; throne: the throne room, each frame of the game. The
; crown on the throne: the blade breaks it, VICTORY
; (CROWN_POINTS, the first byte of the score, and
; ENERGY_POINTS for each unit of energy left). The King:
; - after a blow he flashes for KHIT_FRAMES, and no blow
;   counts; otherwise a blade on him is a blow
;   (KHIT_BCD points), and the KING_HITS-th beats him: the
;   crown takes his place (KING_BCD points), the venom is
;   gone;
; - his bite: their boxes meet and no wound is counting
;   (BITE_DAMAGE);
; - the venom, while it flies: VEN_INT pixels a frame and
;   one more when its fraction carries, on the lines of his
;   mouth; it is gone past its free pixels (VSPAN: stone,
;   the edge) or on Sir Roderick: parried by the shield if
;   it comes from the side he faces and he is not thrusting
;   (he shows the parry for PARRY_FRAMES), else a wound
;   (VENOM_DAMAGE) unless one is counting;
; - otherwise he goes a step of 2 lines (when the fraction
;   of KSTEP_FRAC carries) towards the top line that puts
;   his mouth at Sir Roderick's middle (ky + 2, kept between
;   KING_T0 and KING_T1); when the time before a spit is
;   over and he is there, he spits towards Sir Roderick's
;   side: the venom starts beside him, and the time before
;   the next spit is shorter the more blows he has had
;   (SPIT).

throne: lda     SCR+SC_CROWN
        beq     tr_king
        cmp     #1
        bne     tr_end          ; its pieces: VICTORY is on
        lda     #CROWN_TOP      ; the crown: the blade?
        sta     tmp
        lda     #CROWN_H+1
        sta     tmp+1
        ldx     #4
        jsr     blade_on
        bcs     tr_end
        lda     #2              ; it breaks
        sta     SCW+SC_CROWN
        lda     #1
        sta     won
        lda     #SFX_VICTORY
        sta     sfxreq
        sed                     ; 10 000: the first byte
        lda     score
        clc
        adc     #1
        sta     score
        cld
        ldx     energy          ; for each unit left
        beq     tr_end
tr_en:  lda     #ENERGY_BCD
        jsr     points
        dex
        bne     tr_en
tr_end: rts

tr_king:
        ; - the flash of a blow, or a blow
        lda     SCR+SC_KF
        beq     tr_blow
        sec
        sbc     #1
        sta     SCW+SC_KF
        jmp     tr_bite
tr_blow:
        lda     SCR+SC_KT
        sta     tmp
        lda     #KING_H+1
        sta     tmp+1
        ldx     #0
        jsr     blade_on
        bcs     tr_bite
        lda     #KHIT_FRAMES
        sta     SCW+SC_KF
        lda     #SFX_KING_HIT
        sta     sfxreq
        lda     #KHIT_BCD
        jsr     points
        lda     SCR+SC_KH
        clc
        adc     #1
        sta     SCW+SC_KH
        cmp     #KING_HITS
        bne     tr_bite
        lda     #1              ; beaten: the crown
        sta     SCW+SC_CROWN
        lda     #0
        sta     SCW+SC_VD
        lda     #SFX_KING_DIES
        sta     sfxreq
        lda     #KING_BCD
        jmp     points
        ; - his bite
tr_bite:
        lda     hurt
        bne     tr_venom
        lda     ky              ; lines: ky + 23 - top from
        clc                     ; 0 to 62
        adc     #KNIGHT_H-1
        sec
        sbc     SCR+SC_KT
        cmp     #KNIGHT_H+KING_H-1
        bcs     tr_venom
        lda     kx              ; columns: a run of his
        sec
        sbc     #KBITE_X0
        cmp     #KBITE_N
        bcs     tr_venom
        lda     #BITE_DAMAGE
        jsr     wound
        lda     #SFX_BITE
        sta     sfxreq
        ; - the venom
tr_venom:
        lda     SCR+SC_VD
        bne     tr_fly
        jmp     tr_move
tr_fly: lda     SCR+SC_VA       ; the step of this frame
        clc
        adc     #VEN_FRAC
        sta     SCW+SC_VA
        lda     #VEN_INT
        adc     #0
        sta     tmp
        lda     SCR+SC_KT       ; its span, by his top
        sec                     ; line: (top - KING_T0) / 2
        sbc     #KING_T0
        lsr
        tax
        lda     SCR+SC_VD
        cmp     #1
        bne     tr_vleft
        lda     SCR+SC_VP       ; to the right: its last
        clc                     ; pixel past the span: gone
        adc     tmp
        sta     tmp+1
        adc     #7
        sta     tmp
        lda     VSPAN_HI,x
        cmp     tmp
        bcc     tr_vgone
        lda     tmp+1
        bcs     tr_vset         ; (always)
tr_vleft:
        lda     SCR+SC_VP       ; to the left: its first
        sec                     ; pixel past the screen or
        sbc     tmp             ; the span: gone
        bcc     tr_vgone
        cmp     VSPAN_LO,x
        bcc     tr_vgone
tr_vset:
        sta     SCW+SC_VP
        lda     ky              ; on him? lines: ky + 23 -
        clc                     ; (top + MOUTH) from 0 to 24
        adc     #KNIGHT_H-1-MOUTH
        sec
        sbc     SCR+SC_KT
        cmp     #KNIGHT_H+1
        bcs     tr_vend
        lda     kx              ; pixels: kx + 10 - its
        clc                     ; first from 0 to 14
        adc     #FIRST_PIXEL+KNIGHT_W-1
        sec
        sbc     SCR+SC_VP
        cmp     #KNIGHT_W+7
        bcs     tr_vend
        lda     kpose           ; in the thrust: no parry
        cmp     #THRUST_POSE
        beq     tr_vhit
        lda     SCR+SC_VD       ; the shield: from his left
        lsr                     ; (flying right) if he faces
        lda     kdir            ; left, from his right if he
        bcs     tr_vside        ; faces right
        eor     #8
tr_vside:
        beq     tr_vhit
        lda     #PARRY_FRAMES   ; parried
        sta     parry
        lda     #SFX_PARRY
        sta     sfxreq
        bne     tr_vgone        ; (always)
tr_vhit:
        lda     hurt
        bne     tr_vgone        ; a wound is counting
        lda     #VENOM_DAMAGE
        jsr     wound
        lda     #SFX_BITE
        sta     sfxreq
tr_vgone:
        lda     #0
        sta     SCW+SC_VD
tr_vend:
        rts
        ; - towards Sir Roderick, then the spit
tr_move:
        lda     ky              ; the target: ky + 2, kept
        clc                     ; in KING_T0-KING_T1
        adc     #2
        cmp     #KING_T0
        bcs     tr_t0
        lda     #KING_T0
tr_t0:  cmp     #KING_T1+1
        bcc     tr_t1
        lda     #KING_T1
tr_t1:  sta     tmp
        lda     SCR+SC_ACC      ; a step when it carries
        clc
        adc     #KSTEP_FRAC
        sta     SCW+SC_ACC
        bcc     tr_spit
        lda     SCR+SC_KT
        cmp     tmp
        beq     tr_spit
        bcc     tr_down
        sbc     #2              ; up (carry is set)
        bcs     tr_kt
tr_down:
        adc     #2              ; down (carry is clear)
tr_kt:  sta     SCW+SC_KT
tr_spit:
        lda     SCR+SC_KS       ; the time before a spit
        beq     tr_ready
        sec
        sbc     #1
        sta     SCW+SC_KS
        rts
tr_ready:
        lda     SCR+SC_KT
        cmp     tmp
        bne     tr_wait         ; not there yet
        ldx     #1              ; to his right
        lda     #VEN_RIGHT
        ldy     kx
        cpy     #SPIT_LEFT
        bcs     tr_side
        inx                     ; to his left
        lda     #VEN_LEFT
tr_side:
        sta     SCW+SC_VP
        stx     SCW+SC_VD
        lda     #0
        sta     SCW+SC_VA
        ldx     SCR+SC_KH
        lda     SPIT,x
        sta     SCW+SC_KS
        lda     #SFX_SPIT
        sta     sfxreq
tr_wait:
        rts

; blade_on: carry clear if the blade of a thrust (shown:
; swres 0) is on the lines of a thing (top line in tmp, its
; height + 1 in tmp+1) and on its pixels: Sir Roderick's
; column in a run of BRUN from X (facing right: from BRUN,x
; for BRUN+1,x columns; facing left: BRUN+2,x, BRUN+3,x)
blade_on:
        lda     swres
        bne     bo_no
        lda     ky              ; lines: ky + BLADE_LINE +
        clc                     ; 1 - top from 0 to the
        adc     #BLADE_LINE+1   ; height
        sec
        sbc     tmp
        cmp     tmp+1
        bcs     bo_no
        lda     kdir
        beq     bo_run
        inx
        inx
bo_run: lda     kx
        sec
        sbc     BRUN,x
        cmp     BRUN+1,x
        bcs     bo_no
        rts                     ; (carry is clear: on it)
bo_no:  sec                     ; (carry set: not on it)
        rts

; the runs of Sir Roderick's columns where the blade is on
; the King (from 0) and on the crown (from 4), facing right,
; left
BRUN    .byte   KB_R0, KB_RN, KB_L0, KB_LN
        .byte   CB_R0, CB_RN, CB_L0, CB_LN

; wound: A units of energy less (never below 0), and no
; other wound for BITE_FRAMES (the spikes then set their
; own HURT_FRAMES). Every wound of the game comes here.
wound:  eor     #$FF            ; energy - A
        sec
        adc     energy
        bcs     wo_en
        lda     #0
wo_en:  sta     energy
        lda     #BITE_FRAMES
        sta     hurt
        rts
