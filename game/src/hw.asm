; hw.asm - the registers Scalecrown uses, by name
;
; Written for the game: only the names it needs, with the
; addresses of the TIA and of the RIOT (6532).

; TIA, write side
VSYNC   = $00           ; bit 1: vertical sync
VBLANK  = $01           ; bit 1: picture off
WSYNC   = $02           ; any write: wait for the line end
NUSIZ0  = $04           ; size and copies, player 0 {2}
NUSIZ1  = $05           ; size and copies, player 1 {3}
COLUP0  = $06           ; colour of player 0
COLUP1  = $07           ; colour of player 1 {3}
COLUPF  = $08           ; colour of the playfield
COLUBK  = $09           ; colour of the background
CTRLPF  = $0A           ; bit 0: reflected playfield
REFP0   = $0B           ; bit 3: player 0 mirrored
REFP1   = $0C           ; bit 3: player 1 mirrored {3}
PF0     = $0D           ; playfield, bits 4-7
PF1     = $0E           ; playfield, bits 7-0
PF2     = $0F           ; playfield, bits 0-7
RESP0   = $10           ; any write: player 0 starts here
RESP1   = $11           ; any write: player 1 starts here {4}
RESM0   = $12           ; any write: missile 0 starts here {2}
RESM1   = $13           ; any write: missile 1 starts here {6}
RESBL   = $14           ; any write: the ball starts here {3}
AUDC0   = $15           ; sound, voice 0: waveform (0-15) {7}
AUDC1   = $16           ; voice 1 {7}
AUDF0   = $17           ; voice 0: frequency divider (0-31) {7}
AUDF1   = $18           ; voice 1 {7}
AUDV0   = $19           ; voice 0: volume (0-15) {7}
AUDV1   = $1A           ; voice 1 {7}
GRP0    = $1B           ; graphics of player 0
GRP1    = $1C           ; graphics of player 1 {3}
ENAM0   = $1D           ; bit 1: missile 0 on {2}
ENAM1   = $1E           ; bit 1: missile 1 on {6}
ENABL   = $1F           ; bit 1: the ball on {3}
HMP0    = $20           ; fine move of player 0
HMP1    = $21           ; fine move of player 1 {4}
HMM0    = $22           ; fine move of missile 0 {2}
HMM1    = $23           ; fine move of missile 1 {6}
HMBL    = $24           ; fine move of the ball {3}
VDELP0  = $25           ; bit 0: player 0 delayed {3}
VDELP1  = $26           ; bit 0: player 1 delayed {3}
RESMP0  = $28           ; bit 1: missile 0 off, on player 0 {2}
RESMP1  = $29           ; bit 1: missile 1 off, on player 1 {6}
HMOVE   = $2A           ; any write: apply the fine moves
HMCLR   = $2B           ; any write: clear the fine moves {3}

; TIA, read side {2}
INPT4   = $0C           ; bit 7: left fire button, 0 = down {2}

; RIOT
SWCHA   = $0280         ; joysticks, 0 = pressed {2}
SWCHB   = $0282         ; console switches, 0 = pressed {2}
INTIM   = $0284         ; the timer
TIM64T  = $0296         ; start the timer, 64 cycles a step
