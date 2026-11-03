; dungeon.asm - bank 3: the rooms of the dungeon
;
; The playfield of the 16 rooms (bank3.asm, from
; dungeon.py): 60 bytes each, the order of the Superchip
; RAM (PF0 of the 20 courses, then PF1, then PF2), with the
; grate closed and the plates of the spikes down.
; Bank 7 calls room_copy with jsr TO_COPY when Sir Roderick
; comes into a room; the trampoline in the tail of every
; bank brings it here and takes it back.

; room_copy: the playfield of room `room` into the Superchip
; RAM, from the last byte down. The change of room is the
; heaviest frame of the VBLANK, so the loop is unrolled:
; 60 copies of the three instructions, 12 cycles a byte
; (13 when the load crosses a page) instead of 15 or 16.
room_copy:
        ldx     room
        lda     RS_LO,x
        sta     tmp
        lda     RS_HI,x
        sta     tmp+1
        ldy     #59
        REPEAT  60
        lda     (tmp),y
        sta     SCW,y
        dey
        REPEND
        lda     RDOOR3,x        ; the door of the room open? {4}
        and     opened ; {4}
        beq     rc_done ; {4}
        lda     DOP3,x          ; the bytes of the open {3}
        tax                     ; version (VI3: index, $FF {3}
rc_put: ldy     VI3,x           ; ends; VV3: value) {3}
        bmi     rc_done ; {3}
        lda     VV3,x ; {3}
        sta     SCW,y ; {3}
        inx ; {3}
        bne     rc_put ; {3}
rc_done:
        rts
