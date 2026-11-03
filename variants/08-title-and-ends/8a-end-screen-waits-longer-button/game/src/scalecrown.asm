; scalecrown.asm - Scalecrown
; Step 8 of the chain of the book: the title and the
; end screens
;
; A 32K cartridge with the Superchip (F4SC): eight banks of
; 4K and 128 bytes of RAM in the cartridge.
; The title (bank 1) with three modes of sound: SELECT
; chooses MUSIC, SOUND FX or SILENT; the button or RESET
; starts a game.
; Sir Roderick in the Crypt of Scales: 16 rooms in four
; levels (dungeon.py).
; The joystick moves him, the walls stop him, the button
; thrusts the sword; RESET starts again.
; The openings east and west lead to the rooms beside, the
; stairs to the level below and back; the ball closes the
; outer side of the rooms at the ends of a level. The HUD:
; the score, the energy, the name of the level.
; The things: a chest in each level gives the key of the
; level's door (a grate on the stair down; the golden gate
; before the throne room); spikes go up and down in eight
; rooms; points for chests and doors.
; The serpents: one or two in a room, crawling to and fro,
; faster in the lower levels; a bite takes energy, and so
; do the spikes; a wound makes him flash; energy 0: GAME
; OVER.
; A thrust of the sword kills a serpent (they are back
; when he comes in again).
; Player 1 shows two things: the kernel moves it in the
; middle of the room (the seam) to the serpent of the band
; below; two things in the same lines take turns.
; The Serpent King: in the throne room, drawn by its own
; kernel (bank 2), he goes up and down to meet Sir
; Roderick and spits venom (missile 1) at him; the oak
; shield parries what comes from the side Sir Roderick
; faces. Ten blows beat the King; the crown appears on the
; throne; struck, it breaks: VICTORY.
; The sound (bank 5): the theme, and the effects of the
; sword, the stairs, the things, the bites and the blows.
; After GAME OVER or VICTORY the end screen (bank 6) with
; the score; the button goes back to the title, RESET
; starts a game. A lament for GAME OVER and a fanfare for
; VICTORY play once (MUSIC); a new song, as a new mode,
; first silences what played.
;
; Banks (the address of each one for the 6507):
;   0 ($1000) the room: kernel, figures, colours
;   1 ($3000) the title: kernel, letters
;   2 ($5000) the throne room: its kernel, the King, the
;             crown, its colours
;   3 ($7000) the rooms: their playfield, the copy
;   4 ($9000) the things: chests, doors, spikes
;             the serpents, the Serpent King
;   5 ($B000) sound: player, music, effects
;   6 ($D000) the end screens: their kernel, the crown
;             whole and broken, the words, scenes
;   7 ($F000) start, frame, logic, HUD, room tables
; Every bank starts with the 256 bytes of the Superchip
; window and ends with the same tail (trampolines, reset).
; Banks 0 and 2 then start with the same bytes: Sir
; Roderick's figures and colours (kfig0.asm, kfig2.asm), so
; that the pointers to them work in both kernels.
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
SC_SX   = 60            ; the guards: columns (two),
SC_SD   = 62            ; facing: 0 right, 8 left (two),
SC_LIVE = 64            ; alive: bit 0 the first, bit 1 the
                        ; second;
SC_ACC  = 65            ; the fraction of their crawl (the
                        ; King's steps);
SC_HM   = 66            ; HMP1 for the seam (the fine move)
SC_KT   = 67            ; the Serpent King: top line,
SC_KH   = 68            ; blows he has had,
SC_KF   = 69            ; frames of his flash after a blow,
SC_KS   = 70            ; frames before he spits;
SC_VP   = 71            ; the venom: its first pixel,
SC_VD   = 72            ; 0 none, 1 flying right, 2 left,
SC_VA   = 73            ; the fraction of its flight;
SC_CROWN = 74           ; 0 the King, 1 the crown, 2 broken
                        ; (new_game: 0; it stays when he
                        ; leaves the throne room)

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
screen  ds 1            ; 0 title, 1-16 a room (room + 1)
shown   ds 1            ; the screen set up in the SC
held    ds 1            ; buttons down a frame ago
pressed ds 1            ; pressed now: fire $80, SELECT $02,
                        ; RESET $01
room    ds 1            ; 0-15: level room / 4 + 1
score   ds 3            ; BCD, six digits (things.asm
                        ; adds the points)
energy  ds 1            ; 0-12 (things.asm: the wounds)
; == Sir Roderick (knight.asm)
kx      ds 1            ; column, 0-149
ky      ds 1            ; top line, odd, 1-135
kdir    ds 1            ; 0 right, 8 left (REFP0)
kpose   ds 1            ; 0 stand, 1-2 steps, 3 thrust
kdist   ds 1            ; units walked: pose of the walk
hacc    ds 1            ; fraction of a step: sideways,
vacc    ds 1            ; up and down
thrust  ds 1            ; frames of the thrust still to go
parry   ds 1            ; frames of the parry still to
                        ; go (things.asm starts it)
moved   ds 1            ; he moved in this frame
swx     ds 1            ; the blade: column, NUSIZ0, RESMP0
swnus   ds 1
swres   ds 1
; == player 1, the plug (main.asm: setup_room,
; == p1_bands: the thing of band A)
ox      ds 1            ; column
oy      ds 1            ; top line (odd)
odir    ds 1            ; 0 right, 8 left (REFP1)
okind   ds 1            ; first frame in the OG tables
onus    ds 1            ; NUSIZ1 in the room
plug    ds 1            ; ENABL in the room: 2 the ball
; == the things (things.asm; new_game and setup_room
; == start them)
key     ds 1            ; the key he has: its level, 0 none
opened  ds 1            ; open: chests bits 0-3, doors 4-7
spk     ds 1            ; frames left before the plates turn
spup    ds 1            ; the plates: 0 down, 1 up
hurt    ds 1            ; frames before a wound can come
                        ; again (the spikes, a bite)
; == the collision test (knight.asm: box_free, wall)
cmap    ds 2            ; collision map of the room
                        ; (main.asm: room_state)
nx      ds 1            ; the box tried: column, top line
ny      ds 1
bc0     ds 1            ; its block columns, left, right
bc1     ds 1
br      ds 1            ; 3 x the block row tested (its
                        ; first byte in the map)
; == sound (sound.asm; mode: main.asm, SELECT on the title;
; == sfxreq: knight.asm asks, sound.asm clears; song:
; == main.asm and things.asm)
mode    ds 1            ; 0 MUSIC, 1 SOUND FX, 2 SILENT
smode   ds 1            ; the mode the player last saw ($FF:
                        ; a song to start)
song    ds 1            ; 2 x the song (main.asm,
                        ; things.asm choose it)
sfxreq  ds 1            ; effect asked for (0: none)
sfxi    ds 1            ; effect playing: its frame, 0 none
mclock  ds 1            ; frames left in this step
mstep   ds 1            ; index in STEPLEN
vpos    ds 2            ; each voice: offset in its stream,
vleft   ds 2            ; steps left of its note,
venv    ds 2            ; frame of the note (envelope),
vins    ds 2            ; instrument,
vnote   ds 2            ; note (0: a rest)
; == the seam of player 1 (main.asm prepares;
; == room_kernel.asm)
zcnt    ds 1            ; courses to the seam (0: none)
zcoarse ds 1            ; the delay before RESP1 there
zref    ds 1            ; REFP1 below the seam
s2gfx   ds 2            ; player 1 below the seam: graphics,
s2col   ds 2            ; colours
; == GAME OVER, VICTORY (things.asm sets them, main.asm
; == counts)
over    ds 1            ; 0 playing, else 1 + frames since
                        ; it began, up to GO_FRAMES
won     ds 1            ; the same for VICTORY, up to
                        ; VIC_FRAMES
; == the kernels (main.asm prepares; room_kernel.asm)
kgfx    ds 2            ; Sir Roderick: graphics, colours
kcol    ds 2
sgfx    ds 2            ; player 1: graphics, colours
scol    ds 2
cbk     ds 2            ; room colours: COLUBK, COLUPF
cpf     ds 2
zbk     ds 1            ; COLUBK of the next line A
zt      ds 1            ; colour for Y at the end of a line
zc1     ds 1            ; COLUP1 of the next line B
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
; == scratch (anyone; never kept across a call; the room
; == kernel keeps a value of the seam in tmp)
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

; --- bank 0: the room -------------------------------------
        BANK    0
        include "kfig0.asm"
        include "room_kernel.asm"
        include "bank0.asm"
bank0_end
        TAIL    0

; --- bank 1: title ----------------------------------------
        BANK    1
        include "title_kernel.asm"
        include "bank1.asm"
bank1_end
        TAIL    1

; --- bank 2: the throne room ------------------------------
        BANK    2
        include "kfig2.asm"
        ; Sir Roderick at the same place as in bank 0
        IF KFG_2-$4000 != KFG || KFG_END_2-$4000 != KFG_END
        ERR
        ENDIF
        include "throne_kernel.asm"
        include "bank2.asm"
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
        include "things.asm"
        include "bank4.asm"
bank4_end
        TAIL    4
; --- bank 5: sound ---------------------------------------
        BANK    5
        include "sound.asm"
        include "bank5.asm"
bank5_end
        TAIL    5
; --- bank 6: the end screens ----------------------------
        BANK    6
        include "ends_kernel.asm"
        include "bank6.asm"
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
