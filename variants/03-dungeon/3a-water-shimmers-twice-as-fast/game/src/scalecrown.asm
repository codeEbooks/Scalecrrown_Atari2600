; scalecrown.asm - Scalecrown
; Step 3 of the chain of the book: the dungeon
;
; A 32K cartridge with the Superchip (F4SC): eight banks of
; 4K and 128 bytes of RAM in the cartridge.
; Sir Roderick in the Crypt of Scales: 16 rooms in four
; levels (dungeon.py).
; The joystick moves him, the walls stop him, the button
; thrusts the sword; RESET starts again.
; The openings east and west lead to the rooms beside, the
; stairs to the level below and back; the ball closes the
; outer side of the rooms at the ends of a level. The HUD:
; the score, the energy, the name of the level.
; The doors are open.
;
; Banks (the address of each one for the 6507):
;   0 ($1000) the room: kernel, figures, colours
;   1 ($3000) the title: only its tail before step 8
;   2 ($5000) the throne room: only its tail before
;             step 6
;   3 ($7000) the rooms: their playfield, the copy
;   4 ($9000) the things: only its tail before step 4
;   5 ($B000) sound: only its tail before step 7
;   6 ($D000) the end screens: only its tail before
;             step 8
;   7 ($F000) start, frame, logic, HUD, room tables
; Every bank starts with the 256 bytes of the Superchip
; window and ends with the same tail (trampolines, reset).
;
;   dasm scalecrown.asm -f3 -S -I../assets/generated
;        [-DPAL=1]

        processor 6502
        include "hw.asm"

        IFNCONST PAL
PAL     = 0
        ENDIF

        IF PAL
TOP_BLANK  = 18         ; black lines above the HUD
BOT_BLANK  = 18         ; and below the room
VBLANK_TIM = 54
OVER_TIM   = 43
        ELSE
TOP_BLANK  = 0
BOT_BLANK  = 0
VBLANK_TIM = 44
OVER_TIM   = 35
        ENDIF

; F4: an access to $1FF4 + n selects bank n
F4B0    = $1FF4
F4B1    = $1FF5
F4B2    = $1FF6
F4B3    = $1FF7
F4B4    = $1FF8
F4B5    = $1FF9
F4B6    = $1FFA
F4B7    = $1FFB
; Superchip: written at $1000-$107F, read at $1080-$10FF
SCW     = $1000
SCR     = $1080
SC_PF0  = 0             ; the room: PF0 of the 20 courses,
SC_PF1  = 20            ; course c at index 19 - c
SC_PF2  = 40

; trampolines, the same addresses in every bank
TO_ENDS  = $1FAA        ; -> bank 6, ends_kernel
TO_THRONE = $1FB0       ; -> bank 2, throne_kernel
TO_THINGS = $1FB6       ; jsr: bank 4, things, back to 7
TO_ROOM  = $1FC0        ; -> bank 0, room_kernel
TO_TITLE = $1FC6        ; -> bank 1, title_kernel
TO_MAIN  = $1FCC        ; -> bank 7, kernel_done
TO_SOUND = $1FD2        ; jsr: bank 5, sound, back to 7
TO_COPY  = $1FE6        ; jsr: bank 3, room_copy, back

SCORE_X  = 51           ; the six digits of the HUD
FIRST_PIXEL = 3         ; a player: first pixel = column + 3
M_OFFSET = 2            ; a missile: column + 2
KNIGHT_W = 8            ; Sir Roderick: 8 x 24
KNIGHT_H = 24

; ---------------------------------------------------------
; RAM: 128 bytes, $80-$FF, the stack at the top
;
; Every variable has one owner, the part of the program
; that writes it (the others read it); the groups below say
; which.

        SEG.U   ram
        ORG     $80
; == state (main.asm): frame, screens, buttons, the game
; == (knight.asm changes room and screen on the way out)
frames  ds 1            ; frame counter
screen  ds 1            ; 1-16: a room (room + 1)
shown   ds 1            ; the screen set up in the SC
held    ds 1            ; buttons down a frame ago
pressed ds 1            ; pressed now: fire $80, SELECT $02,
                        ; RESET $01
room    ds 1            ; 0-15: level room / 4 + 1
score   ds 3            ; BCD, six digits
energy  ds 1            ; 0-12: the bar of the HUD
; == Sir Roderick (knight.asm)
kx      ds 1            ; column, 0-149
ky      ds 1            ; top line, odd, 1-135
kdir    ds 1            ; 0 right, 8 left (REFP0)
kpose   ds 1            ; 0 stand, 1-2 steps, 3 thrust
kdist   ds 1            ; units walked: pose of the walk
hacc    ds 1            ; fraction of a step: sideways,
vacc    ds 1            ; up and down
thrust  ds 1            ; frames of the thrust still to go
moved   ds 1            ; he moved in this frame
swx     ds 1            ; the blade: column, NUSIZ0, RESMP0
swnus   ds 1
swres   ds 1
; == the plug (main.asm: setup_room)
plug    ds 1            ; ENABL in the room: 2 the ball
; == the collision test (knight.asm: box_free, wall)
cmap    ds 2            ; collision map of the room
                        ; (main.asm: room_state)
nx      ds 1            ; the box tried: column, top line
ny      ds 1
bc0     ds 1            ; its block columns, left, right
bc1     ds 1
br      ds 1            ; 3 x the block row tested (its
                        ; first byte in the map)
; == the kernels (main.asm prepares; room_kernel.asm)
kgfx    ds 2            ; Sir Roderick: graphics, colours
kcol    ds 2
cbk     ds 2            ; room colours: COLUBK, COLUPF
cpf     ds 2
zbk     ds 1            ; COLUBK of the next line A
zt      ds 1            ; colour for Y at the end of a line
idx     ds 1            ; index of the line being prepared
trow    ds 1            ; Superchip index of the next course
znpf0   ds 1            ; PF0, PF1, PF2 of the next course
znpf1   ds 1
znpf2   ds 1
; == the HUD (main.asm prepares; hud.asm)
dig     ds 12           ; the six columns of digits
txp     ds 12           ; and of the name of the level
zt2     ds 1
bar1    ds 1            ; energy bar: PF1, PF2
bar2    ds 1
; == scratch (anyone; never kept across a call)
tmp     ds 2
ram_end

; ---------------------------------------------------------
; the banks

        MAC BANK        ; {1}: bank number
        SEG     bank{1}
        ORG     {1}*$1000
        RORG    $1000+{1}*$2000
        ds      256, 0          ; the Superchip window
        ENDM

        MAC TAIL        ; {1}: bank number
        ORG     {1}*$1000+$FAA
        RORG    $1FAA+{1}*$2000
        sta     F4B6            ; $FAA: to the end screens
        jmp     ends_kernel
        sta     F4B2            ; $FB0: to the throne kernel
        jmp     throne_kernel
        sta     F4B4            ; $FB6: (jsr here) bank 4
        jsr     things          ; $FB9: in bank 4
        sta     F4B7            ; $FBC: bank 7 again
        rts                     ; $FBF: in bank 7
        sta     F4B0            ; $FC0: to the room kernel
        jmp     room_kernel
        sta     F4B1            ; $FC6: to the title kernel
        jmp     title_kernel
        sta     F4B7            ; $FCC: back to the frame
        jmp     kernel_done
        sta     F4B5            ; $FD2: (jsr here) bank 5
        jsr     sound           ; $FD5: in bank 5
        sta     F4B7            ; $FD8: bank 7 again
        rts                     ; $FDB: in bank 7
        ORG     {1}*$1000+$FE0
        RORG    $1FE0+{1}*$2000
        sta     F4B7            ; $FE0: reset, in any bank
        jmp     start
        sta     F4B3            ; $FE6: (jsr here) bank 3
        jsr     room_copy       ; $FE9: in bank 3
        sta     F4B7            ; $FEC: bank 7 again
        rts                     ; $FEF: in bank 7
        ORG     {1}*$1000+$FFC
        RORG    $1FFC+{1}*$2000
        .word   $1FE0+{1}*$2000
        .word   $1FE0+{1}*$2000
        ENDM

; A bank whose code comes in a later step has only its
; tail, and the routine its trampoline goes to is a stub:
; never called before that step.

; --- bank 0: the room -------------------------------------
        BANK    0
        include "kfig0.asm"
        include "room_kernel.asm"
        include "bank0.asm"
bank0_end
        TAIL    0

; --- bank 1: title ----------------------------------------
        BANK    1
title_kernel:                  ; (step 8)
        jmp     TO_MAIN
bank1_end
        TAIL    1

; --- bank 2: the throne room ------------------------------
        BANK    2
throne_kernel:                 ; (step 6)
        jmp     TO_MAIN
bank2_end
        TAIL    2
; --- bank 3: the rooms -----------------------------------
        BANK    3
        include "dungeon.asm"
        include "bank3.asm"
bank3_end
        TAIL    3
; --- bank 4: the things ----------------------------------
        BANK    4
things:                        ; (step 4)
        rts
bank4_end
        TAIL    4
; --- bank 5: sound ---------------------------------------
        BANK    5
sound:                         ; (step 7)
        rts
bank5_end
        TAIL    5
; --- bank 6: the end screens ----------------------------
        BANK    6
ends_kernel:                   ; (step 8)
        jmp     TO_MAIN
bank6_end
        TAIL    6

; --- bank 7: start, frame, logic, HUD ---------------------
        BANK    7
        include "main.asm"
        include "knight.asm"
        include "hud.asm"
        include "bank7.asm"
bank7_end
        TAIL    7
