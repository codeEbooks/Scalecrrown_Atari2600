; knight.asm - bank 7: Sir Roderick
;
; One frame of his: while he parries the venom with his {6}
; shield (things.asm starts it) he stands still and shows {6}
; the parry; {6}
; the button starts a thrust of the sword, during which he
; stands still; otherwise the joystick moves him, first
; left or right, then up or down, each direction tried on
; its own against the walls (so he slides along a wall
; when pushed diagonally into it). Past the edge of the {3}
; screen he goes into the next room: east and west {3}
; through the openings, down and up by the stairs. {3}
;|; when pushed diagonally into it); the edges of the {2-2}
;|; screen stop him as the walls do. {2-2}
; The speeds are in bank7.asm, one table for each
; television (rules.py).

        IF V_INT != 0
        ERR                     ; one step at most per frame
        ENDIF
        IF STRIDE != 8
        ERR                     ; the walk divides by 8
        ENDIF

knight:
        lda     parry           ; the parry {6}
        beq     kn_thrust ; {6}
        dec     parry ; {6}
        lda     #PARRY_POSE ; {6}
        sta     kpose ; {6}
        rts ; {6}
kn_thrust:
        lda     thrust
        beq     kn_fire
        dec     thrust
        bne     kn_pose3        ; still thrusting
kn_fire:
        bit     pressed         ; bit 7: the button
        bpl     kn_walk
        lda     #THRUST_FRAMES
        sta     thrust
        lda     #SFX_SWORD      ; the sound of the sword {7}
        sta     sfxreq          ; (in the SOUND FX mode) {7}
kn_pose3:
        lda     #THRUST_POSE
        sta     kpose
        rts

kn_walk:
        lda     #0
        sta     moved
        lda     SWCHA           ; right $80, left $40, down
        sta     tmp+1           ; $20, up $10: 0 = pushed
        and     #$C0
        cmp     #$C0
        beq     kn_vert         ; neither left nor right
        lda     hacc            ; pixels in this frame:
        clc                     ; H_INT, one more when the
        adc     #H_FRAC         ; fraction carries
        sta     hacc
        lda     #H_INT
        adc     #0
        sta     tmp
        bit     tmp+1
        bmi     kn_left         ; right not pushed: left
        lda     #0
        sta     kdir            ; facing right
        lda     kx
        clc
        adc     tmp
        cmp     #X_MAX+1
        bcs     kn_east         ; past the edge: next room {3}
;|        bcs     kn_vert         ; the edge: he stays {2-2}
        bcc     kn_htry
kn_left:
        lda     #8
        sta     kdir            ; facing left
        lda     kx
        sec
        sbc     tmp
        bcc     kn_west         ; past the edge: room before {3}
;|        bcc     kn_vert         ; the edge: he stays {2-2}
kn_htry:
        sta     nx
        lda     ky
        sta     ny
        jsr     box_free
        bcs     kn_vert         ; stone: he stays
        lda     nx
        sta     kx
kn_walked:
        lda     kdist           ; the walk goes on
        clc
        adc     tmp
        sta     kdist
        lda     #1
        sta     moved
kn_vert:
        lda     tmp+1
        and     #$30
        cmp     #$30
        beq     kn_pose         ; neither up nor down
        lda     vacc            ; a step in this frame when
        clc                     ; the fraction carries
        adc     #V_FRAC
        sta     vacc
        bcc     kn_pose
        lda     tmp+1
        and     #$10
        bne     kn_down         ; up not pushed: down
        lda     ky
        cmp     #TOP_MIN+2
        bcc     kn_up           ; at the top: the stair up {3}
;|        bcc     kn_pose         ; at the top: he stays {2-2}
        sbc     #2              ; (carry is set)
        bcs     kn_vtry
kn_down:
        lda     ky
        cmp     #TOP_MAX
        bcs     kn_downst       ; at the bottom: down {3}
;|        bcs     kn_pose         ; at the bottom: he {2-2}
;|                                ; stays {2-2}
        adc     #2              ; (carry is clear)
kn_vtry:
        sta     ny
        lda     kx
        sta     nx
        jsr     box_free
        bcs     kn_pose         ; stone: he stays
        lda     ny
        sta     ky
        inc     kdist
        lda     #1
        sta     moved
kn_pose:                ; walking: WALK, a pose every
        lda     moved           ; 8 units; standing: pose 0
        beq     kn_stand
        lda     kdist
        lsr
        lsr
        lsr
        and     #3
        tax
        lda     WALK,x
kn_stand:
        sta     kpose
        rts

; Through an opening: the room beside; he comes in on the {3}
; other side, at the same height. There is always a room {3}
; there: at the ends of a level the plug keeps him from {3}
; the edge (dungeon.py). In this frame he does not go up or {3}
; down. {3}
kn_east: ; {3}
        ldx     room ; {3}
        inx                     ; the room east {3}
        lda     #0              ; in on the west side {3}
        beq     kn_room ; {3}
kn_west: ; {3}
        ldx     room ; {3}
        dex                     ; the room west {3}
        lda     #X_MAX          ; in on the east side {3}
kn_room: ; {3}
        sta     kx ; {3}
        stx     room ; {3}
        inx ; {3}
        stx     screen          ; setup_room sees the change {3}
        lda     #$FF            ; no up or down this frame {3}
        sta     tmp+1 ; {3}
        bne     kn_walked ; {3}

; By a stair: he can be at the top or the bottom of the {3}
; screen only in a gap of the top or bottom wall. Down from {3}
; a south gap there is always the room below (a stair); up {3}
; from a north gap the room above, except in the first {3}
; level, where the north gap of room 1 is the broken gate of {3}
; Oakhaven: nothing is above it. He comes in at the other {3}
; end of the screen, in the same column; the move is a step. {3}
kn_downst: ; {3}
        lda     room ; {3}
        adc     #GRID-1         ; + GRID (carry is set) {3}
        ldx     #TOP_MIN        ; in at the top {3}
        bne     kn_stair ; {3}
kn_up: ; {3}
        lda     room ; {3}
        cmp     #GRID ; {3}
        bcc     kn_pose         ; the first level: he stays {3}
        sbc     #GRID           ; (carry is set) {3}
        ldx     #TOP_MAX        ; in at the bottom {3}
kn_stair: ; {3}
        stx     ky ; {3}
        sta     room ; {3}
        tax ; {3}
        inx ; {3}
        stx     screen          ; setup_room sees the change {3}
        inc     kdist ; {3}
        lda     #1 ; {3}
        sta     moved ; {3}
        lda     #SFX_STAIR      ; the steps (in the SOUND FX {7}
        sta     sfxreq          ; mode) {7}
        bne     kn_pose ; {3}

; ---------------------------------------------------------
; box_free: carry clear if Sir Roderick fits at column nx,
; top line ny: no block under his 8 x 24 box is stone. The
; box touches block columns (nx + 3) / 8 and (nx + 10) / 8,
; block rows ny / 16, (ny + 12) / 16 and (ny + 23) / 16
; (24 lines can touch three rows of 16, never four).

box_free:
        lda     nx
        clc
        adc     #FIRST_PIXEL
        lsr
        lsr
        lsr
        sta     bc0             ; left edge
        lda     nx
        clc
        adc     #FIRST_PIXEL+KNIGHT_W-1
        lsr
        lsr
        lsr
        sta     bc1             ; right edge
        lda     ny
        jsr     bf_row          ; top line
        bcs     bf_done
        lda     ny
        clc
        adc     #KNIGHT_H/2
        jsr     bf_row          ; middle
        bcs     bf_done
        lda     ny
        clc
        adc     #KNIGHT_H-1     ; bottom line, and back
bf_row: lsr                     ; A: a line of the box
        lsr
        lsr
        lsr                     ; its block row (0-9)
        sta     br
        asl                     ; (clears the carry)
        adc     br
        sta     br              ; 3 x the row: its byte 0
        lda     bc0
        jsr     wall
        bne     bf_stone
        lda     bc1
        jsr     wall
        bne     bf_stone
        clc                     ; free
        rts
bf_stone:
        sec
bf_done:
        rts

; wall: Z clear (bne) if block column A (0-19) is stone in
; the block row whose first byte is br. The collision map
; has three bytes a row, the whole width (the plug closes
; one side only): columns 0-7 in the first byte, 8-15 in
; the second, 16-19 in the third, the first column in
; bit 7.
wall:   tax                     ; the column
        lsr
        lsr
        lsr                     ; its byte in the row, 0-2
        clc
        adc     br
        tay
        txa
        and     #7              ; its bit
        tax
        lda     (cmap),y
        and     BITS,x
        rts

BITS    .byte   $80, $40, $20, $10, $08, $04, $02, $01

; ---------------------------------------------------------
; blade: where missile 0 goes. In the thrust it is 8 pixels
; beside the hand: right of the figure facing right, left
; of it facing left; near the edge of the screen 4, 2 or 1
; (NUSIZ0 bits 4-5). Otherwise it is hidden: RESMP0 = 2
; keeps it on player 0, switched off.

blade:
        lda     #2
        sta     swres           ; hidden
        lda     kpose
        cmp     #THRUST_POSE
        bne     bl_done
        ldx     #3              ; width: 8 pixels
        lda     kdir
        bne     bl_left
        lda     kx              ; first pixel right of him
        clc
        adc     #FIRST_PIXEL+KNIGHT_W
        cmp     #160
        bcs     bl_done         ; no room at all: hidden
        cmp     #160-7
        bcc     bl_set          ; 8 pixels
        dex
        cmp     #160-3
        bcc     bl_set          ; 4
        dex
        cmp     #160-1
        bcc     bl_set          ; 2
        dex                     ; 1
        bcs     bl_set
bl_left:                        ; it ends at pixel kx + 2
        lda     kx
        sec
        sbc     #KNIGHT_W-FIRST_PIXEL
        bcs     bl_set          ; 8 pixels from kx - 5
        dex
        adc     #4              ; kx - 1 (carry clear)
        bcs     bl_set          ; 4 pixels, if kx >= 1
        dex
        lda     #1              ; kx = 0: 2 pixels, 1 and 2
bl_set:                         ; A: first pixel, X: width
        sec
        sbc     #M_OFFSET       ; the column that puts it
        bcs     bl_col          ; there
        adc     #160            ; (round the screen)
bl_col: sta     swx
        lda     BLADE_NUS,x
        sta     swnus
        lda     #0
        sta     swres           ; shown
bl_done:
        rts

BLADE_NUS .byte $00, $10, $20, $30      ; 1, 2, 4, 8 pixels
