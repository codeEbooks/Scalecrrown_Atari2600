; sound.asm - bank 5: the sound player
;
; Called once a frame in the overscan, from bank 7 through
; the trampoline TO_SOUND (in the tail of every bank).
; Three modes, chosen with SELECT (main.asm):
;   0 MUSIC     the theme on both voices (voice 0 the bass,
;               voice 1 the melody), no effects
;   1 SOUND FX  the effects on voice 0, voice 1 silent
;   2 SILENT    nothing
; When the mode changes both voices are silenced, any effect
; stops and the music starts again from its first step.
;
; The song: the theme; song is 2 x the one playing. To
; start it the game writes it in song and $FF in smode
; (RESET): the player sees a new mode and does as above.
;
; The music (music.py makes the tables from score.py): each
; voice reads a stream of bytes: $FE n chooses instrument
; n; a note (index in NOTE_C / NOTE_F, 0 is a rest) and its
; length in steps; $FF goes back to the voice's loop point.
; A step is a sixteenth note: STEPLEN frames (NTSC 9; PAL 8
; and 7 in turn). The volume of a note follows its
; instrument's envelope, one value a frame (the last holds);
; the last frame of every note is silent.
;
; The effects (sfx.py): AUDC, AUDF, AUDV of each frame in
; three tables, an AUDC of $FF at the end. The game
; asks for one with sfxreq; sfxi is the frame playing.

sound:
        lda     mode
        cmp     smode
        beq     so_mode
        sta     smode           ; a new mode: silence, the
        ldx     #0              ; music from the start, no
        stx     AUDV0           ; effect
        stx     AUDV1
        stx     sfxi
        stx     mclock
        stx     mstep
        stx     vpos
        stx     vpos+1
        stx     vleft
        stx     vleft+1
so_mode:
        lda     mode
        beq     music
        cmp     #1
        beq     effects
        lda     #0              ; SILENT
        sta     AUDV0
        sta     AUDV1
        sta     sfxreq
        rts

; --- SOUND FX ---------------------------------------------

effects:
        lda     #0
        sta     AUDV1           ; voice 1 rests
        ldx     sfxreq
        beq     ef_play
        sta     sfxreq          ; (A is 0)
        lda     SFX_START-1,x   ; a new effect, at its start
        sta     sfxi
ef_play:
        ldy     sfxi
        lda     SFX_C,y         ; AUDC, or $FF at the end
        bmi     ef_end
        sta     AUDC0
        lda     SFX_F,y
        sta     AUDF0
        lda     SFX_V,y
        sta     AUDV0
        iny
        sty     sfxi
        rts
ef_end: rts
        sta     AUDV0
        sta     sfxi            ; frame 0: the empty effect
        rts

; --- MUSIC ------------------------------------------------

music:
        lda     #0
        sta     sfxreq          ; no effects in this mode
        lda     mclock
        bne     mu_frame
        ldx     mstep           ; a new step
        lda     STEPLEN,x
        sta     mclock
        inx
        cpx     #STEPS_N
        bcc     mu_step
        ldx     #0
mu_step:
        stx     mstep
        ldx     #1
mu_next:
        lda     vleft,x         ; voice X: its note over,
        bne     mu_dec          ; the next one
        jsr     fetch
mu_dec: dec     vleft,x         ; steps left after this one
        dex
        bpl     mu_next
mu_frame:
        dec     mclock          ; 0: a step's last frame
        ldx     #1
mu_vol: lda     #0
        ldy     vnote,x
        beq     mu_set          ; a rest
        ldy     vleft,x
        bne     mu_on
        ldy     mclock
        beq     mu_set          ; the last frame of the note
mu_on:  ldy     vins,x
        lda     venv,x
        cmp     ENV_LAST,y      ; the envelope goes on until
        bcs     mu_hold         ; its last value
        inc     venv,x
        bcc     mu_read         ; (inc leaves C clear)
mu_hold:
        lda     ENV_LAST,y
mu_read:
        clc
        adc     ENV_START,y
        tay
        lda     ENV_DATA,y
mu_set: sta     AUDV0,x
        dex
        bpl     mu_vol
        rts

; fetch: the next note of voice X, through the pointer tmp
; (the stream of voice X of the song: 2 x song + X)
fetch:  txa
        clc
        adc     song
        tay
        lda     VS_LO,y
        sta     tmp
        lda     VS_HI,y
        sta     tmp+1
fe_byte:
        ldy     vpos,x
        lda     (tmp),y
        cmp     #$FE
        bcc     fe_note         ; a note or a rest
        beq     fe_ins
        txa                     ; $FF: to the loop point
        clc
        adc     song
        tay
        lda     VLOOP,y
        sta     vpos,x
        jmp     fe_byte
fe_ins: iny                     ; $FE: an instrument
        lda     (tmp),y
        sta     vins,x
        iny
        sty     vpos,x
        jmp     fe_byte
fe_note:
        sta     vnote,x
        iny
        lda     (tmp),y
        sta     vleft,x         ; its steps
        iny
        sty     vpos,x
        lda     #0
        sta     venv,x
        ldy     vnote,x
        beq     fe_done         ; a rest
        lda     NOTE_C,y
        sta     AUDC0,x
        lda     NOTE_F,y
        sta     AUDF0,x
fe_done:
        rts
