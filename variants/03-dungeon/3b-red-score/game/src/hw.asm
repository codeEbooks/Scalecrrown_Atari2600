; hw.asm - the registers Scalecrown uses, by name
;
; Written for the game: only the names it needs, with the
; addresses of the TIA and of the RIOT (6532).

; TIA, write side
VSYNC   = $00           ; bit 1: vertical sync
VBLANK  = $01           ; bit 1: picture off
WSYNC   = $02           ; any write: wait for the line end
NUSIZ0  = $04           ; size and copies, player 0
NUSIZ1  = $05           ; size and copies, player 1
COLUP0  = $06           ; colour of player 0
COLUP1  = $07           ; colour of player 1
COLUPF  = $08           ; colour of the playfield
COLUBK  = $09           ; colour of the background
CTRLPF  = $0A           ; bit 0: reflected playfield
REFP0   = $0B           ; bit 3: player 0 mirrored
REFP1   = $0C           ; bit 3: player 1 mirrored
PF0     = $0D           ; playfield, bits 4-7
PF1     = $0E           ; playfield, bits 7-0
PF2     = $0F           ; playfield, bits 0-7
RESP0   = $10           ; any write: player 0 starts here
RESM0   = $12           ; any write: missile 0 starts here
RESBL   = $14           ; any write: the ball starts here
GRP0    = $1B           ; graphics of player 0
GRP1    = $1C           ; graphics of player 1
ENAM0   = $1D           ; bit 1: missile 0 on
ENABL   = $1F           ; bit 1: the ball on
HMP0    = $20           ; fine move of player 0
HMM0    = $22           ; fine move of missile 0
HMBL    = $24           ; fine move of the ball
VDELP0  = $25           ; bit 0: player 0 delayed
VDELP1  = $26           ; bit 0: player 1 delayed
RESMP0  = $28           ; bit 1: missile 0 off, on player 0
HMOVE   = $2A           ; any write: apply the fine moves
HMCLR   = $2B           ; any write: clear the fine moves

; TIA, read side
INPT4   = $0C           ; bit 7: left fire button, 0 = down

; RIOT
SWCHA   = $0280         ; joysticks, 0 = pressed
SWCHB   = $0282         ; console switches, 0 = pressed
INTIM   = $0284         ; the timer
TIM64T  = $0296         ; start the timer, 64 cycles a step
