; palette.asm - every colour of the TIA, one per line, for
; tools/stella_palette.py: line k of the picture has colour
; 2(k-1) (line 0 keeps black). 4K, NTSC or PAL (-DPAL=1).
        processor 6502
        include "hw.asm"
        IFNCONST PAL
PAL     = 0
        ENDIF
        IF PAL
VB = 54
OV = 43
VIS = 228
        ELSE
VB = 44
OV = 35
VIS = 192
        ENDIF
        SEG code
        ORG $F000
start:  sei
        cld
        ldx #0
        txa
clr:    sta 0,x
        dex
        bne clr
main:   lda #2
        sta WSYNC
        sta VSYNC
        sta VBLANK
        sta WSYNC
        sta WSYNC
        lsr
        sta WSYNC
        sta VSYNC
        lda #VB
        sta TIM64T
w1:     lda INTIM
        bne w1
        sta WSYNC
        sta VBLANK
        ldy #0
k:      tya
        asl
        bcc ok
        lda #0
ok:     sta WSYNC
        sta COLUBK
        iny
        cpy #VIS
        bne k
        sta WSYNC
        lda #0
        sta COLUBK
        lda #2
        sta VBLANK
        lda #OV
        sta TIM64T
w2:     lda INTIM
        bne w2
        jmp main
        ORG $FFFC
        .word start
        .word start
