; things.asm - bank 4: the things of the rooms, the guards {5}
; and the Serpent King {6}
;|; and the serpents {5-5}
;|; things.asm - bank 4: the things of the rooms {4-4}
;
; Called once a frame in the overscan of a game, from bank 7
; through the trampoline TO_THINGS, before the sound: what {7}
;|; through the trampoline TO_THINGS: what {4-6}
; Sir Roderick's move of this frame did, after the picture
; that showed it.
; - The spikes: the time of the plates. setup_room
;   (main.asm) starts them down when he comes into a room;
;   when they turn, their version of the two courses goes
;   into the Superchip RAM, where the kernel draws the room
;   from.
; - The hurt: on a raised plate he loses SPIKE_DAMAGE units {5}
;   of energy, again every HURT_FRAMES while he stays on {5}
;   it. While the count of a wound goes down (after the {5}
;   spikes or a bite) nothing hurts him, and he flashes. {5}
; - The guards, each one alive: the blade of a thrust {5}
;   wounds a serpent it touches: the first blow pushes it {9}
;   back and stuns it, the second kills it (SERPENT_BCD {9}
;   points); {9}
;|;   kills a serpent it touches (SERPENT_BCD points); {5-8}
;   a serpent whose box touches his bites (BITE_DAMAGE, {5}
;   then BITE_FRAMES without wounds); then they crawl {5}
;   along their paths, turning at the ends, at the speed of {5}
;   the room (a fraction of a pixel a frame), or chase him {9}
;   with a sprint. A dead one comes back after {9}
;   RESPAWN_FRAMES. {9}
;|;   the room (a fraction of a pixel a frame). {5-8}
;   The column of the first guard, for the seam of the {5}
;   next frame (zcoarse, SC_HM). {5}
; - The thing of the room: a chest he touches opens and
;   gives him the key of the level; a door he stands in
;   front of with that key opens (the key is used up), and
;   the open version of the grate goes into the Superchip
;   RAM. Points for both, and their sound in the SOUND FX {7}
;   mode. {7}
;|;   RAM. Points for both. {4-6}
; - The throne room, in place of the guards: the Serpent {6}
;   King (throne, below) or the crown. {6}
;|; - The throne room has nothing (the King: step 6). {5-5}
; - GAME OVER: energy 0. From then on nothing here; nor {6}
;   after VICTORY. {6}
;|; - GAME OVER: energy 0. From then on nothing here. {5-5}
; What player 1 shows, the collision map and the key in the
; HUD follow in the next frame (room_state, p1_bands in
; main.asm).
;
; The tables (bank4.asm, from dungeon.py and rules.py): for
; each room its lists of versions, the bit of its thing in
; `opened`, where he touches it, where the plates are; {5}
; its guards (32 entries: r the first, 16 + r the second). {5}
;|; `opened`, where he touches it, where the plates are. {4-4}

        IF CHEST_BCD == 0 || SPK_UP == 0
        ERR                     ; (the branches below)
        ENDIF

things:
        lda     over            ; GAME OVER, VICTORY: all {6}
;|        lda     over            ; GAME OVER: all stops {5-5}
        ora     won             ; stops {6}
        beq     th_go ; {5}
        rts ; {5}
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
        ; --- the hurt: while it counts down, no new one {5}
th_hurt:
        lda     hurt ; {5}
        beq     th_feet ; {5}
        dec     hurt ; {5}
        bne     th_guards ; {5}
th_feet: ; {5}
        lda     spup ; {5}
        beq     th_guards       ; the plates are down {5}
        lda     ky ; {5}
        cmp     #PLATE_Y0 ; {5}
        bcc     th_guards ; {5}
        cmp     #PLATE_Y1 ; {5}
        bcs     th_guards       ; his feet off their lines {5}
        ldx     room ; {5}
        lda     kx              ; the middle of his feet {5}
        cmp     PXA0,x          ; over the first plate {5}
        bcc     th_plb ; {5}
        cmp     PXA1,x ; {5}
        bcc     th_hit ; {5}
th_plb: cmp     PXB0,x          ; or over the second {5}
        bcc     th_guards ; {5}
        cmp     PXB1,x ; {5}
        bcs     th_guards ; {5}
th_hit: lda     #SPIKE_DAMAGE   ; a wound (the routine of {5}
        jsr     wound           ; every wound), with the {5}
        lda     #HURT_FRAMES    ; rest of the spikes {5}
        sta     hurt ; {5}
        lda     #SFX_HURT ; {7}
        sta     sfxreq ; {7}
        ; --- the guards, the King {6}
;|        ; --- the guards {5-5}
th_guards: ; {5}
        ldx     room ; {5}
        cpx     #THRONE_ROOM ; {5}
        bne     th_serp ; {6}
;|        beq     th_thing        ; (the King: step 6) {5-5}
        jsr     throne ; {6}
        jmp     th_thing ; {6}
th_serp: ; {6}
        jsr     guards ; {5}
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
        lda     #SFX_CHEST ; {7}
        sta     sfxreq ; {7}
        lda     #CHEST_BCD
        bne     th_points
th_door:
        cpy     key             ; a door: only with the key
        bne     th_done         ; of its level
        ora     opened
        sta     opened
        lda     #0
        sta     key             ; the key is used up
        lda     #SFX_DOOR ; {7}
        sta     sfxreq ; {7}
        lda     DOP4,x          ; the grate opens (the gate:
        tax                     ; an empty list)
        jsr     put
        lda     #DOOR_BCD
th_points:
        jsr     points
        ; --- GAME OVER: energy 0 {5}
th_done:
        lda     energy ; {5}
        bne     th_end ; {5}
        lda     #1 ; {5}
        sta     over ; {5}
        lda     #0              ; he stands, no flash {5}
        sta     hurt ; {5}
        sta     kpose ; {5}
        sta     thrust ; {5}
        sta     parry           ; no parry, the venom is {6}
        sta     SCW+SC_VD       ; gone {6}
        lda     #SFX_GAMEOVER ; {7}
        sta     sfxreq ; {7}
        lda     #SONG_GAMEOVER  ; the lament (MUSIC) {8}
        sta     song ; {8}
        lda     #$FF            ; (a new song: the player {8}
        sta     smode           ; silences what played) {8}
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

; --------------------------------------------------------- {5}
; guards: the guards of the room one after the other, each {5}
; with X its entry in the tables (r, then 16 + r) and Y its {5}
; place in the Superchip (0, 1); all serpents. tmp+1: bit {5}
; 0, they crawl a pixel in this frame (the fraction of the {5}
; room's speed carries); bits 1-2, the pixels of the sprint {9}
; of a chase in this frame: SPRI and the carry of SPRF, 0-2. {9}
;|; room's speed carries). {5-8}

guards: ldx     room ; {5}
        lda     SCR+SC_ACC ; {5}
        clc ; {5}
        adc     CRAWL,x ; {5}
        sta     SCW+SC_ACC ; {5}
        lda     #0 ; {5}
        rol ; {5}
        sta     tmp+1 ; {5}
        lda     SCR+SC_SPR      ; the sprint {9}
        clc ; {9}
        adc     SPRF,x ; {9}
        sta     SCW+SC_SPR ; {9}
        lda     SPRI,x ; {9}
        adc     #0 ; {9}
        asl ; {9}
        ora     tmp+1 ; {9}
        sta     tmp+1 ; {9}
        ldy     #0              ; the first guard {5}
gu_one: lda     GBIT,y ; {5}
        and     SCR+SC_LIVE ; {5}
        beq     gu_dead         ; dead {9}
;|        beq     gu_next         ; dead {5-8}
        lda     S_TOP4,x ; {5}
        beq     gu_next         ; none {5}
        jsr     guard ; {5}
gu_next: ; {5}
        txa ; {5}
        ora     #16             ; the second {5}
        tax ; {5}
        iny ; {5}
        cpy     #2 ; {5}
        bcc     gu_one ; {5}
        ; the column of the first guard for the seam of {5}
        ; the next frame: the delay (5 cycles a count) and {5}
        ; the fine move, as place does it for the column - 3 {5}
        ; (the RESP1 of the seam writes a cycle after {5}
        ; place's: 3 pixels more; a guard below a seam is {5}
        ; never left of column 3) {5}
        lda     SCR+SC_SX ; {5}
        sec ; {5}
        sbc     #3 ; {5}
        ldy     #0 ; {5}
gu_div: iny ; {5}
        sbc     #15 ; {5}
        bcs     gu_div ; {5}
        eor     #7 ; {5}
        asl ; {5}
        asl ; {5}
        asl ; {5}
        asl ; {5}
        sta     SCW+SC_HM ; {5}
        sty     zcoarse ; {5}
        rts ; {5}
        ; - the return: a dead guard counts down; {9}
        ; at 0 it comes back (one never killed counts 0) {9}
gu_dead: ; {9}
        lda     SCR+SC_GT,y ; {9}
        beq     gu_next ; {9}
        sec ; {9}
        sbc     #1 ; {9}
        sta     SCW+SC_GT,y ; {9}
        bne     gu_next ; {9}
        jsr     respawn ; {9}
        jmp     gu_next ; {9}

GBIT    .byte   1, 2            ; in SC_LIVE: alive, {9}
;|GBIT    .byte   1, 2            ; their bits in SC_LIVE {5-8}
WBIT    .byte   4, 8            ; wounded {9}

; respawn: guard X/Y alive and unwounded again, at {9}
; the end of its path farther from him, facing the other end {9}
respawn: ; {9}
        lda     S_MIN4,x ; {9}
        clc ; {9}
        adc     S_MAX4,x ; {9}
        ror                     ; the middle of its path {9}
        cmp     kx ; {9}
        bcc     re_min          ; he is right of the middle {9}
        lda     S_MAX4,x ; {9}
        sta     SCW+SC_SX,y ; {9}
        lda     #8 ; {9}
        bne     re_face ; {9}
re_min: lda     S_MIN4,x ; {9}
        sta     SCW+SC_SX,y ; {9}
        lda     #0 ; {9}
re_face: ; {9}
        sta     SCW+SC_SD,y ; {9}
        lda     GBIT,y          ; alive (the wound went when {9}
        ora     SCR+SC_LIVE     ; it died) {9}
        sta     SCW+SC_LIVE ; {9}
        rts ; {9}

; guard: one guard alive, X its entry, Y its place {5}
        ; - stunned after the first blow, it only {9}
        ; counts down (no blade, no bite, no crawl) {9}
guard:  lda     SCR+SC_GT,y ; {9}
        beq     ga_blade ; {9}
        sec ; {9}
        sbc     #1 ; {9}
        sta     SCW+SC_GT,y ; {9}
        rts ; {9}
;|guard: {5-8}
        ; - the blade: in a thrust (shown: swres 0), on the {5}
        ; lines ky + BLADE_LINE and the one after, 1 to 15 {5}
        ; columns from him on the side he faces (with the {5}
        ; guards 16 columns from the edges this is where the {5}
        ; 8 pixels of the blade touch the guard's 8) {5}
ga_blade: ; {9}
        lda     swres ; {5}
        bne     ga_bite ; {5}
        lda     ky ; {5}
        clc ; {5}
        adc     #BLADE_LINE+1 ; {5}
        sec ; {5}
        sbc     S_TOP4,x ; {5}
        cmp     #SERPENT_H+1    ; its lines and the guard's {5}
        bcs     ga_bite         ; meet: 0-16 {5}
        lda     kdir ; {5}
        bne     ga_left ; {5}
        lda     SCR+SC_SX,y     ; facing right: the guard's {5}
        sec                     ; column - his {5}
        sbc     kx ; {5}
        bcs     ga_dist         ; (below: the guard is left {5}
        bcc     ga_bite         ; of him) {5}
ga_left: ; {5}
        lda     kx              ; facing left: his - the {5}
        sec                     ; guard's {5}
        sbc     SCR+SC_SX,y ; {5}
        bcc     ga_bite ; {5}
ga_dist: ; {5}
        sbc     #1              ; (carry is set) {5}
        cmp     #15 ; {5}
        bcs     ga_bite         ; not 1-15 columns {5}
        jmp     ga_blow         ; a blow (it takes two) {9}
;|        lda     GBIT,y          ; killed {5-8}
;|        eor     #$FF {5-8}
;|        and     SCR+SC_LIVE {5-8}
;|        sta     SCW+SC_LIVE {5-8}
;|        lda     #SFX_KILL {7-8}
;|        sta     sfxreq {7-8}
;|        lda     #SERPENT_BCD {5-8}
;|        jmp     points {5-8}
        ; - the bite: their boxes meet (8 x 24, 8 x 16), and {5}
        ; no wound is counting down {5}
ga_bite: ; {5}
        lda     hurt ; {5}
        bne     ga_crawl ; {5}
        lda     ky              ; lines: ky + 23 - top from {5}
        clc                     ; 0 to 38 {5}
        adc     #KNIGHT_H-1 ; {5}
        sec ; {5}
        sbc     S_TOP4,x ; {5}
        cmp     #KNIGHT_H+SERPENT_H-1 ; {5}
        bcs     ga_crawl ; {5}
        lda     kx              ; columns: kx - column + 7 {5}
        sec                     ; from 0 to 14 {5}
        sbc     SCR+SC_SX,y ; {5}
        clc ; {5}
        adc     #KNIGHT_W-1 ; {5}
        cmp     #2*KNIGHT_W-1 ; {5}
        bcs     ga_crawl ; {5}
        lda     #BITE_DAMAGE    ; bitten {5}
        jsr     wound ; {5}
        lda     #SFX_BITE ; {7}
        sta     sfxreq ; {7}
        ; - the crawl {9}
        ; the chase: a serpent on his lines (as for the {9}
        ; bite: ky + 23 - top from 0 to 38), with his column {9}
        ; on its path, faces him and crawls towards him (the {9}
        ; sprint, 0-2 pixels a frame); on his column it {9}
        ; waits. Otherwise its round: a pixel when the {9}
        ; fraction carries, turning at the ends {9}
;|        ; - the crawl: a pixel when the fraction carries {5-8}
ga_crawl: ; {5}
        lda     ky ; {9}
        clc ; {9}
        adc     #KNIGHT_H-1 ; {9}
        sec ; {9}
        sbc     S_TOP4,x ; {9}
        cmp     #KNIGHT_H+SERPENT_H-1 ; {9}
        bcs     ga_round        ; not on his lines {9}
        lda     kx ; {9}
        cmp     S_MIN4,x ; {9}
        bcc     ga_round        ; left of its path {9}
        lda     S_MAX4,x ; {9}
        cmp     kx ; {9}
        bcc     ga_round        ; right of its path {9}
        lda     tmp+1 ; {9}
        and     #6              ; the sprint, 2 x 0-2 {9}
        beq     ga_done ; {9}
        cmp     #4 ; {9}
        bne     ga_step ; {9}
        jsr     ga_step         ; two pixels {9}
ga_step: ; {9}
        lda     kx ; {9}
        cmp     SCR+SC_SX,y ; {9}
        beq     ga_done         ; on his column: it waits {9}
        lda     #0              ; his column right of its {9}
        bcs     ga_face         ; own: to the right {9}
        lda     #8 ; {9}
ga_face: ; {9}
        sta     SCW+SC_SD,y ; {9}
        bne     ga_cleft ; {9}
        lda     SCR+SC_SX,y     ; right (his column is on {9}
        clc                     ; the path: never past {9}
        adc     #1              ; its end) {9}
        sta     SCW+SC_SX,y ; {9}
        rts ; {9}
ga_cleft: ; {9}
        lda     SCR+SC_SX,y     ; left (the same) {9}
        sec ; {9}
        sbc     #1 ; {9}
        sta     SCW+SC_SX,y ; {9}
        rts ; {9}
ga_round: ; {9}
        lda     tmp+1 ; {5}
        lsr ; {5}
        bcc     ga_done         ; no pixel in this frame {5}
        ; - the way back and forth; at the end of its path {5}
        ; it turns (also where a chase left it) {9}
;|        ; it turns {5-8}
ga_way: lda     SCR+SC_SD,y ; {5}
        bne     ga_cl ; {5}
        lda     SCR+SC_SX,y     ; to the right {5}
        cmp     S_MAX4,x ; {5}
        bcs     ga_tl           ; at the end: it turns {5}
        adc     #1              ; (carry is clear) {5}
        sta     SCW+SC_SX,y ; {5}
        cmp     S_MAX4,x ; {5}
        bne     ga_done ; {5}
ga_tl:  lda     #8              ; it turns {5}
        sta     SCW+SC_SD,y ; {5}
        rts ; {5}
ga_cl:  lda     SCR+SC_SX,y     ; to the left {5}
        cmp     S_MIN4,x ; {5}
        beq     ga_tr           ; at the end: it turns {5}
        sbc     #1              ; (carry is set) {5}
        sta     SCW+SC_SX,y ; {5}
        cmp     S_MIN4,x ; {5}
        bne     ga_done ; {5}
ga_tr:  lda     #0 ; {5}
        sta     SCW+SC_SD,y ; {5}
ga_done: ; {5}
        rts ; {5}
        ; - a blow: wounded already? {9}
ga_blow: ; {9}
        lda     WBIT,y ; {9}
        and     SCR+SC_LIVE ; {9}
        bne     ga_kill ; {9}
        ; - the first blow: wounded, stunned, pushed {9}
        ; KNOCK_PX away along its path, facing him {9}
        lda     WBIT,y ; {9}
        ora     SCR+SC_LIVE ; {9}
        sta     SCW+SC_LIVE ; {9}
        lda     #STUN_FRAMES ; {9}
        sta     SCW+SC_GT,y ; {9}
        lda     #SFX_KING_HIT ; {9}
        sta     sfxreq ; {9}
        lda     kdir ; {9}
        bne     ga_pushl ; {9}
        lda     #8              ; he faces right: pushed {9}
        sta     SCW+SC_SD,y     ; right, it faces left {9}
        lda     SCR+SC_SX,y ; {9}
        clc ; {9}
        adc     #KNOCK_PX ; {9}
        cmp     S_MAX4,x ; {9}
        bcc     ga_pset ; {9}
        lda     S_MAX4,x        ; (the end of its path) {9}
        bcs     ga_pset ; {9}
ga_pushl: ; {9}
        lda     #0              ; he faces left: pushed {9}
        sta     SCW+SC_SD,y     ; left, it faces right {9}
        lda     SCR+SC_SX,y ; {9}
        sec ; {9}
        sbc     #KNOCK_PX ; {9}
        cmp     S_MIN4,x ; {9}
        bcs     ga_pset ; {9}
        lda     S_MIN4,x ; {9}
ga_pset: ; {9}
        sta     SCW+SC_SX,y ; {9}
        rts ; {9}
        ; - the second blow kills it; it comes back in a {9}
        ; while {9}
ga_kill: ; {9}
        lda     GBIT,y ; {9}
        ora     WBIT,y ; {9}
        eor     #$FF ; {9}
        and     SCR+SC_LIVE ; {9}
        sta     SCW+SC_LIVE ; {9}
        lda     #RESPAWN_FRAMES ; {9}
        sta     SCW+SC_GT,y ; {9}
        lda     #SFX_KILL ; {9}
        sta     sfxreq ; {9}
        lda     #SERPENT_BCD ; {9}
        jmp     points ; {9}

; --------------------------------------------------------- {6}
; throne: the throne room, each frame of the game. The {6}
; crown on the throne: the blade breaks it, VICTORY {6}
; (CROWN_POINTS, the first byte of the score, and {6}
; ENERGY_POINTS for each unit of energy left). The King: {6}
; - after a blow he flashes for KHIT_FRAMES, and no blow {6}
;   counts; otherwise a blade on his head (his first {9}
;   KING_HEAD lines, where the venom flies) is a blow {9}
;|;   counts; otherwise a blade on him is a blow {6-8}
;   (KHIT_BCD points), and the KING_HITS-th beats him: the {6}
;   crown takes his place (KING_BCD points), the venom is {6}
;   gone; {6}
; - his bite: their boxes meet and no wound is counting {6}
;   (BITE_DAMAGE); {6}
; - the venom, while it flies: VEN_INT pixels a frame and {6}
;   one more when its fraction carries, on the lines of his {6}
;   mouth; it is gone past its free pixels (VSPAN: stone, {6}
;   the edge) or on Sir Roderick: parried by the shield if {6}
;   it comes from the side he faces and he is not thrusting {6}
;   (he shows the parry for PARRY_FRAMES), else a wound {6}
;   (VENOM_DAMAGE) unless one is counting; {6}
; - otherwise he goes a step of 2 lines (when the fraction {6}
;   of KSTEP_FRAC carries) towards the top line that puts {6}
;   his mouth at Sir Roderick's middle (ky + 2, kept between {6}
;   KING_T0 and KING_T1); when the time before a spit is {6}
;   over and he is there, he spits towards Sir Roderick's {6}
;   side: the venom starts beside him, and the time before {6}
;   the next spit is shorter the more blows he has had {6}
;   (SPIT). {6}

throne: lda     SCR+SC_CROWN ; {6}
        beq     tr_king ; {6}
        cmp     #1 ; {6}
        bne     tr_end          ; its pieces: VICTORY is on {6}
        lda     #CROWN_TOP      ; the crown: the blade? {6}
        sta     tmp ; {6}
        lda     #CROWN_H+1 ; {6}
        sta     tmp+1 ; {6}
        ldx     #4 ; {6}
        jsr     blade_on ; {6}
        bcs     tr_end ; {6}
        lda     #2              ; it breaks {6}
        sta     SCW+SC_CROWN ; {6}
        lda     #1 ; {6}
        sta     won ; {6}
        lda     #SFX_VICTORY ; {7}
        sta     sfxreq ; {7}
        lda     #SONG_VICTORY   ; the fanfare (MUSIC) {8}
        sta     song ; {8}
        lda     #$FF ; {8}
        sta     smode ; {8}
        sed                     ; 10 000: the first byte {6}
        lda     score ; {6}
        clc ; {6}
        adc     #1 ; {6}
        sta     score ; {6}
        cld ; {6}
        ldx     energy          ; for each unit left {6}
        beq     tr_end ; {6}
tr_en:  lda     #ENERGY_BCD ; {6}
        jsr     points ; {6}
        dex ; {6}
        bne     tr_en ; {6}
tr_end: rts ; {6}

tr_king: ; {6}
        ; - the flash of a blow, or a blow {6}
        lda     SCR+SC_KF ; {6}
        beq     tr_blow ; {6}
        sec ; {6}
        sbc     #1 ; {6}
        sta     SCW+SC_KF ; {6}
        jmp     tr_bite ; {6}
tr_blow: ; {6}
        lda     SCR+SC_KT ; {6}
        sta     tmp ; {6}
        lda     #KING_HEAD+1    ; his head only {9}
;|        lda     #KING_H+1 {6-8}
        sta     tmp+1 ; {6}
        ldx     #0 ; {6}
        jsr     blade_on ; {6}
        bcs     tr_bite ; {6}
        lda     #KHIT_FRAMES ; {6}
        sta     SCW+SC_KF ; {6}
        lda     #SFX_KING_HIT ; {7}
        sta     sfxreq ; {7}
        lda     #KHIT_BCD ; {6}
        jsr     points ; {6}
        lda     SCR+SC_KH ; {6}
        clc ; {6}
        adc     #1 ; {6}
        sta     SCW+SC_KH ; {6}
        cmp     #KING_HITS ; {6}
        bne     tr_bite ; {6}
        lda     #1              ; beaten: the crown {6}
        sta     SCW+SC_CROWN ; {6}
        lda     #0 ; {6}
        sta     SCW+SC_VD ; {6}
        lda     #SFX_KING_DIES ; {7}
        sta     sfxreq ; {7}
        lda     #KING_BCD ; {6}
        jmp     points ; {6}
        ; - his bite {6}
tr_bite: ; {6}
        lda     hurt ; {6}
        bne     tr_venom ; {6}
        lda     ky              ; lines: ky + 23 - top from {6}
        clc                     ; 0 to 62 {6}
        adc     #KNIGHT_H-1 ; {6}
        sec ; {6}
        sbc     SCR+SC_KT ; {6}
        cmp     #KNIGHT_H+KING_H-1 ; {6}
        bcs     tr_venom ; {6}
        lda     kx              ; columns: a run of his {6}
        sec ; {6}
        sbc     #KBITE_X0 ; {6}
        cmp     #KBITE_N ; {6}
        bcs     tr_venom ; {6}
        lda     #BITE_DAMAGE ; {6}
        jsr     wound ; {6}
        lda     #SFX_BITE ; {7}
        sta     sfxreq ; {7}
        ; - the venom {6}
tr_venom: ; {6}
        lda     SCR+SC_VD ; {6}
        bne     tr_fly ; {6}
        jmp     tr_move ; {6}
tr_fly: lda     SCR+SC_VA       ; the step of this frame {6}
        clc ; {6}
        adc     #VEN_FRAC ; {6}
        sta     SCW+SC_VA ; {6}
        lda     #VEN_INT ; {6}
        adc     #0 ; {6}
        sta     tmp ; {6}
        lda     SCR+SC_KT       ; its span, by his top {6}
        sec                     ; line: (top - KING_T0) / 2 {6}
        sbc     #KING_T0 ; {6}
        lsr ; {6}
        tax ; {6}
        lda     SCR+SC_VD ; {6}
        cmp     #1 ; {6}
        bne     tr_vleft ; {6}
        lda     SCR+SC_VP       ; to the right: its last {6}
        clc                     ; pixel past the span: gone {6}
        adc     tmp ; {6}
        sta     tmp+1 ; {6}
        adc     #7 ; {6}
        sta     tmp ; {6}
        lda     VSPAN_HI,x ; {6}
        cmp     tmp ; {6}
        bcc     tr_vgone ; {6}
        lda     tmp+1 ; {6}
        bcs     tr_vset         ; (always) {6}
tr_vleft: ; {6}
        lda     SCR+SC_VP       ; to the left: its first {6}
        sec                     ; pixel past the screen or {6}
        sbc     tmp             ; the span: gone {6}
        bcc     tr_vgone ; {6}
        cmp     VSPAN_LO,x ; {6}
        bcc     tr_vgone ; {6}
tr_vset: ; {6}
        sta     SCW+SC_VP ; {6}
        lda     ky              ; on him? lines: ky + 23 - {6}
        clc                     ; (top + MOUTH) from 0 to 24 {6}
        adc     #KNIGHT_H-1-MOUTH ; {6}
        sec ; {6}
        sbc     SCR+SC_KT ; {6}
        cmp     #KNIGHT_H+1 ; {6}
        bcs     tr_vend ; {6}
        lda     kx              ; pixels: kx + 10 - its {6}
        clc                     ; first from 0 to 14 {6}
        adc     #FIRST_PIXEL+KNIGHT_W-1 ; {6}
        sec ; {6}
        sbc     SCR+SC_VP ; {6}
        cmp     #KNIGHT_W+7 ; {6}
        bcs     tr_vend ; {6}
        lda     kpose           ; in the thrust: no parry {6}
        cmp     #THRUST_POSE ; {6}
        beq     tr_vhit ; {6}
        lda     SCR+SC_VD       ; the shield: from his left {6}
        lsr                     ; (flying right) if he faces {6}
        lda     kdir            ; left, from his right if he {6}
        bcs     tr_vside        ; faces right {6}
        eor     #8 ; {6}
tr_vside: ; {6}
        beq     tr_vhit ; {6}
        lda     #PARRY_FRAMES   ; parried {6}
        sta     parry ; {6}
        lda     #SFX_PARRY ; {7}
        sta     sfxreq ; {7}
        bne     tr_vgone        ; (always) {6}
tr_vhit: ; {6}
        lda     hurt ; {6}
        bne     tr_vgone        ; a wound is counting {6}
        lda     #VENOM_DAMAGE ; {6}
        jsr     wound ; {6}
        lda     #SFX_BITE ; {7}
        sta     sfxreq ; {7}
tr_vgone: ; {6}
        lda     #0 ; {6}
        sta     SCW+SC_VD ; {6}
tr_vend: ; {6}
        rts ; {6}
        ; - towards Sir Roderick, then the spit {6}
tr_move: ; {6}
        lda     ky              ; the target: ky + 2, kept {6}
        clc                     ; in KING_T0-KING_T1 {6}
        adc     #2 ; {6}
        cmp     #KING_T0 ; {6}
        bcs     tr_t0 ; {6}
        lda     #KING_T0 ; {6}
tr_t0:  cmp     #KING_T1+1 ; {6}
        bcc     tr_t1 ; {6}
        lda     #KING_T1 ; {6}
tr_t1:  sta     tmp ; {6}
        lda     SCR+SC_ACC      ; a step when it carries {6}
        clc ; {6}
        adc     #KSTEP_FRAC ; {6}
        sta     SCW+SC_ACC ; {6}
        bcc     tr_spit ; {6}
        lda     SCR+SC_KT ; {6}
        cmp     tmp ; {6}
        beq     tr_spit ; {6}
        bcc     tr_down ; {6}
        sbc     #2              ; up (carry is set) {6}
        bcs     tr_kt ; {6}
tr_down: ; {6}
        adc     #2              ; down (carry is clear) {6}
tr_kt:  sta     SCW+SC_KT ; {6}
tr_spit: ; {6}
        lda     SCR+SC_KS       ; the time before a spit {6}
        beq     tr_ready ; {6}
        sec ; {6}
        sbc     #1 ; {6}
        sta     SCW+SC_KS ; {6}
        rts ; {6}
tr_ready: ; {6}
        lda     SCR+SC_KT ; {6}
        cmp     tmp ; {6}
        bne     tr_wait         ; not there yet {6}
        ldx     #1              ; to his right {6}
        lda     #VEN_RIGHT ; {6}
        ldy     kx ; {6}
        cpy     #SPIT_LEFT ; {6}
        bcs     tr_side ; {6}
        inx                     ; to his left {6}
        lda     #VEN_LEFT ; {6}
tr_side: ; {6}
        sta     SCW+SC_VP ; {6}
        stx     SCW+SC_VD ; {6}
        lda     #0 ; {6}
        sta     SCW+SC_VA ; {6}
        ldx     SCR+SC_KH ; {6}
        lda     SPIT,x ; {6}
        sta     SCW+SC_KS ; {6}
        lda     #SFX_SPIT ; {7}
        sta     sfxreq ; {7}
tr_wait: ; {6}
        rts ; {6}

; blade_on: carry clear if the blade of a thrust (shown: {6}
; swres 0) is on the lines of a thing (top line in tmp, its {6}
; height + 1 in tmp+1) and on its pixels: Sir Roderick's {6}
; column in a run of BRUN from X (facing right: from BRUN,x {6}
; for BRUN+1,x columns; facing left: BRUN+2,x, BRUN+3,x) {6}
blade_on: ; {6}
        lda     swres ; {6}
        bne     bo_no ; {6}
        lda     ky              ; lines: ky + BLADE_LINE + {6}
        clc                     ; 1 - top from 0 to the {6}
        adc     #BLADE_LINE+1   ; height {6}
        sec ; {6}
        sbc     tmp ; {6}
        cmp     tmp+1 ; {6}
        bcs     bo_no ; {6}
        lda     kdir ; {6}
        beq     bo_run ; {6}
        inx ; {6}
        inx ; {6}
bo_run: lda     kx ; {6}
        sec ; {6}
        sbc     BRUN,x ; {6}
        cmp     BRUN+1,x ; {6}
        bcs     bo_no ; {6}
        rts                     ; (carry is clear: on it) {6}
bo_no:  sec                     ; (carry set: not on it) {6}
        rts ; {6}

; the runs of Sir Roderick's columns where the blade is on {6}
; the King (from 0) and on the crown (from 4), facing right, {6}
; left {6}
BRUN    .byte   KB_R0, KB_RN, KB_L0, KB_LN ; {6}
        .byte   CB_R0, CB_RN, CB_L0, CB_LN ; {6}

; wound: A units of energy less (never below 0), and no {5}
; other wound for BITE_FRAMES (the spikes then set their {5}
; own HURT_FRAMES). Every wound of the game comes here. {5}
wound:  eor     #$FF            ; energy - A {5}
        sec ; {5}
        adc     energy ; {5}
        bcs     wo_en ; {5}
        lda     #0 ; {5}
wo_en:  sta     energy ; {5}
        lda     #BITE_FRAMES ; {5}
        sta     hurt ; {5}
        rts ; {5}
