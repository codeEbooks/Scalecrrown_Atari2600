; hud.asm - bank 7: the HUD, 32 lines above the room
;
; Entered right after the WSYNC that ends the VBLANK, at
; cycle 3 of the first visible line. Draws TOP_BLANK black
; lines (PAL only), then the HUD:
;   lines 0-25   black
;   lines 26-28  Sir Roderick to his column
; and goes on to bank 0 (room_kernel.asm) in line 28.
;
; Cycle counts in the comments: the cycle at which a store
; writes, counted from 0 at the start of the line.

hud:
        lda     #0
        sta     VBLANK          ; the picture starts
        IF TOP_BLANK
        ldy     #TOP_BLANK
hu_top: sta     WSYNC
        dey
        bne     hu_top
        ENDIF
        ldy     #25             ; lines 0-24: black
hu_black:
        sta     WSYNC
        dey
        bne     hu_black
        lda     kx
        sta     WSYNC           ; (the end of line 25)
        ; line 26: Sir Roderick to column kx, as place does
        ; it (the stores take 4 cycles, like sta HMP0,x)
        sec
hu_p0:  sbc     #15
        bcs     hu_p0           ; (hu_p0)
        eor     #7
        asl
        asl
        asl
        asl
        sta.w   HMP0
        sta.w   RESP0           ; 68 at most (kx <= 149)
        sta     WSYNC           ; 71 at most
        ; line 27: empty
        sta     WSYNC
        ; line 28: the fine moves, the room's settings
        sta     HMOVE           ;  2
        lda     kdir
        sta     REFP0
        lda     #0
        sta     COLUP0
        lda     swnus
        sta     NUSIZ0          ; the width of the blade
        jmp     TO_ROOM         ; bank 0
