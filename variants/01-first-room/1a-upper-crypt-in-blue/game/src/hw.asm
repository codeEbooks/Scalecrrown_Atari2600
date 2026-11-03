; hw.asm - the registers Scalecrown uses, by name
;
; Written for the game: only the names it needs, with the
; addresses of the TIA and of the RIOT (6532).

; TIA, write side
VSYNC   = $00           ; bit 1: vertical sync
VBLANK  = $01           ; bit 1: picture off
WSYNC   = $02           ; any write: wait for the line end
COLUP0  = $06           ; colour of player 0
COLUPF  = $08           ; colour of the playfield
COLUBK  = $09           ; colour of the background
CTRLPF  = $0A           ; bit 0: reflected playfield
REFP0   = $0B           ; bit 3: player 0 mirrored
PF0     = $0D           ; playfield, bits 4-7
PF1     = $0E           ; playfield, bits 7-0
PF2     = $0F           ; playfield, bits 0-7
RESP0   = $10           ; any write: player 0 starts here
GRP0    = $1B           ; graphics of player 0
HMP0    = $20           ; fine move of player 0
HMOVE   = $2A           ; any write: apply the fine moves

; RIOT
INTIM   = $0284         ; the timer
TIM64T  = $0296         ; start the timer, 64 cycles a step
