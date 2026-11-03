; things.asm - bank 4: the things of the rooms, the guards
; and the serpents
;
; Called once a frame in the overscan of a game, from bank 7
; through the trampoline TO_THINGS: what
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
;   RAM. Points for both.
; - The throne room has nothing (the King: step 6).
; - GAME OVER: energy 0. From then on nothing here.
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
        lda     over            ; GAME OVER: all stops
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
        ; --- the guards
th_guards:
        ldx     room
        cpx     #THRONE_ROOM
        beq     th_thing        ; (the King: step 6)
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
        lda     #CHEST_BCD
        bne     th_points
th_door:
        cpy     key             ; a door: only with the key
        bne     th_done         ; of its level
        ora     opened
        sta     opened
        lda     #0
        sta     key             ; the key is used up
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
