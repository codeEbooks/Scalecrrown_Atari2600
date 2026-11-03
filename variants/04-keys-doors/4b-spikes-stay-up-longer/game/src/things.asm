; things.asm - bank 4: the things of the rooms
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
; - The thing of the room: a chest he touches opens and
;   gives him the key of the level; a door he stands in
;   front of with that key opens (the key is used up), and
;   the open version of the grate goes into the Superchip
;   RAM. Points for both.
; What player 1 shows, the collision map and the key in the
; HUD follow in the next frame (room_state, p1_bands in
; main.asm).
;
; The tables (bank4.asm, from dungeon.py and rules.py): for
; each room its lists of versions, the bit of its thing in
; `opened`, where he touches it, where the plates are.

        IF CHEST_BCD == 0 || SPK_UP == 0
        ERR                     ; (the branches below)
        ENDIF

things:
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
th_hurt:
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
th_done:
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
