; scalecrown.asm - Scalecrown
;|; Step 1 of the chain of the book: the first room {1-1}
;|; Step 2 of the chain of the book: Sir Roderick {2-2}
;|; Step 3 of the chain of the book: the dungeon {3-3}
;|; Step 4 of the chain of the book: keys and doors {4-4}
;|; Step 5 of the chain of the book: the serpents {5-5}
;|; Step 6 of the chain of the book: the Serpent King {6-6}
;|; Step 7 of the chain of the book: the sound {7-7}
;|; Step 8 of the chain of the book: the title and the {8-8}
;|; end screens {8-8}
; Step 9 of the chain of the book, the last: the hunt; the {9}
; complete game {9}
;
; A 32K cartridge with the Superchip (F4SC): eight banks of
; 4K and 128 bytes of RAM in the cartridge.
; The title (bank 1) with three modes of sound: SELECT {8}
; chooses MUSIC, SOUND FX or SILENT; the button or RESET {8}
; starts a game. {8}
; Sir Roderick in the Crypt of Scales: 16 rooms in four {3}
; levels (dungeon.py). {3}
;|; Sir Roderick in the room where he comes into the {1-2}
;|; Crypt of Scales, The Broken Gate (dungeon.py). {1-2}
;|; He stands where he comes in. {1-1}
; The joystick moves him, the walls stop him, the button {2}
; thrusts the sword; RESET starts again. {2}
;|; The edges of the screen stop him too. {2-2}
; The openings east and west lead to the rooms beside, the {3}
; stairs to the level below and back; the ball closes the {3}
; outer side of the rooms at the ends of a level. The HUD: {3}
; the score, the energy, the name of the level. {3}
;|; The doors are open. {3-3}
; The things: a chest in each level gives the key of the {4}
; level's door (a grate on the stair down; the golden gate {4}
; before the throne room); spikes go up and down in eight {4}
; rooms; points for chests and doors. {4}
; The serpents: one or two in a room, crawling to and fro, {5}
; faster in the lower levels; a bite takes energy, and so {5}
; do the spikes; a wound makes him flash; energy 0: GAME {5}
; OVER. {5}
;|; A thrust of the sword kills a serpent (they are back {5-8}
;|; when he comes in again). {5-8}
; Player 1 shows two things: the kernel moves it in the {5}
; middle of the room (the seam) to the serpent of the band {5}
; below; two things in the same lines take turns. {5}
; The Serpent King: in the throne room, drawn by its own {6}
; kernel (bank 2), he goes up and down to meet Sir {6}
; Roderick and spits venom (missile 1) at him; the oak {6}
; shield parries what comes from the side Sir Roderick {6}
; faces. Ten blows beat the King; the crown appears on the {6}
; throne; struck, it breaks: VICTORY. {6}
;|; After GAME OVER or VICTORY the game stops; RESET {5-7}
;|; starts again. {5-7}
; The sound (bank 5): the theme, and the effects of the {7}
; sword, the stairs, the things, the bites and the blows. {7}
;|; SELECT, in the game, chooses MUSIC, SOUND FX or SILENT. {7-7}
; After GAME OVER or VICTORY the end screen (bank 6) with {8}
; the score; the button goes back to the title, RESET {8}
; starts a game. A lament for GAME OVER and a fanfare for {8}
; VICTORY play once (MUSIC); a new song, as a new mode, {8}
; first silences what played. {8}
; The hunt: a serpent on Sir Roderick's lines chases him {9}
; along its path, sprinting; it takes two blows (the first {9}
; pushes it back and stuns it) and comes back a while after {9}
; it dies. The King is struck only on his head. {9}
;
; Banks (the address of each one for the 6507):
;   0 ($1000) the room: kernel, figures, colours
;   1 ($3000) the title: kernel, letters {8}
;|;   1 ($3000) the title: only its tail before step 8 {1-7}
;   2 ($5000) the throne room: its kernel, the King, the {6}
;             crown, its colours {6}
;|;   2 ($5000) the throne room: only its tail before {1-5}
;|;             step 6 {1-5}
;   3 ($7000) the rooms: their playfield, the copy
;   4 ($9000) the things: chests, doors, spikes {4}
;             the serpents, the Serpent King {4}
;|;   4 ($9000) the things: only its tail before step 4 {1-3}
;   5 ($B000) sound: player, music, effects {7}
;|;   5 ($B000) sound: only its tail before step 7 {1-6}
;   6 ($D000) the end screens: their kernel, the crown {8}
;             whole and broken, the words, scenes {8}
;|;   6 ($D000) the end screens: only its tail before {1-7}
;|;             step 8 {1-7}
;   7 ($F000) start, frame, logic, HUD, room tables
; Every bank starts with the 256 bytes of the Superchip
; window and ends with the same tail (trampolines, reset).
; Banks 0 and 2 then start with the same bytes: Sir {6}
; Roderick's figures and colours (kfig0.asm, kfig2.asm), so {6}
; that the pointers to them work in both kernels. {6}
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
SC_SX   = 60            ; the guards: columns (two), {5}
SC_SD   = 62            ; facing: 0 right, 8 left (two), {5}
SC_LIVE = 64            ; alive: bit 0 the first, bit 1 the {5}
                        ; second; {5}
SC_ACC  = 65            ; the fraction of their crawl (the {5}
                        ; King's steps); {5}
SC_HM   = 66            ; HMP1 for the seam (the fine move) {5}
SC_KT   = 67            ; the Serpent King: top line, {6}
SC_KH   = 68            ; blows he has had, {6}
SC_KF   = 69            ; frames of his flash after a blow, {6}
SC_KS   = 70            ; frames before he spits; {6}
SC_VP   = 71            ; the venom: its first pixel, {6}
SC_VD   = 72            ; 0 none, 1 flying right, 2 left, {6}
SC_VA   = 73            ; the fraction of its flight; {6}
SC_CROWN = 74           ; 0 the King, 1 the crown, 2 broken {6}
                        ; (new_game: 0; it stays when he {6}
                        ; leaves the throne room) {6}
SC_GT   = 75            ; the guards: frames of the stun {9}
                        ; after the first blow, or before {9}
                        ; a dead one returns (two); {9}
SC_SPR  = 77            ; the fraction of the sprint {9}

; trampolines, the same addresses in every bank
TO_ENDS  = $1FAA        ; -> bank 6, ends_kernel
TO_THRONE = $1FB0       ; -> bank 2, throne_kernel
TO_THINGS = $1FB6       ; jsr: bank 4, things, back to 7
TO_ROOM  = $1FC0        ; -> bank 0, room_kernel
TO_TITLE = $1FC6        ; -> bank 1, title_kernel
TO_MAIN  = $1FCC        ; -> bank 7, kernel_done
TO_SOUND = $1FD2        ; jsr: bank 5, sound, back to 7
TO_COPY  = $1FE6        ; jsr: bank 3, room_copy, back

SCORE_X  = 51           ; the six digits of the HUD {3}
FIRST_PIXEL = 3         ; a player: first pixel = column + 3 {2}
M_OFFSET = 2            ; a missile: column + 2 {2}
KNIGHT_W = 8            ; Sir Roderick: 8 x 24 {2}
KNIGHT_H = 24 ; {2}

; ---------------------------------------------------------
; RAM: 128 bytes, $80-$FF, the stack at the top
;
; Every variable has one owner, the part of the program
; that writes it (the others read it); the groups below say
; which.

        SEG.U   ram
        ORG     $80
; == state (main.asm): frame, screens, buttons, the game {2}
;|; == state (main.asm): frame, screens, the game {1-1}
; == (knight.asm changes room and screen on the way out) {3}
frames  ds 1            ; frame counter
screen  ds 1            ; 0 title, 1-16 a room (room + 1) {8}
;|screen  ds 1            ; 1-16: a room (room + 1) {1-7}
shown   ds 1            ; the screen set up in the SC
held    ds 1            ; buttons down a frame ago {2}
pressed ds 1            ; pressed now: fire $80, SELECT $02, {2}
                        ; RESET $01 {2}
room    ds 1            ; 0-15: level room / 4 + 1
score   ds 3            ; BCD, six digits (things.asm {4}
                        ; adds the points) {4}
;|score   ds 3            ; BCD, six digits {3-3}
energy  ds 1            ; 0-12 (things.asm: the wounds) {5}
;|energy  ds 1            ; 0-12: the bar of the HUD {3-4}
; == Sir Roderick (knight.asm) {2}
;|; == Sir Roderick (main.asm: new_game) {1-1}
kx      ds 1            ; column, 0-149
ky      ds 1            ; top line, odd, 1-135
kdir    ds 1            ; 0 right, 8 left (REFP0)
kpose   ds 1            ; 0 stand, 1-2 steps, 3 thrust {2}
;|kpose   ds 1            ; 0: he stands {1-1}
kdist   ds 1            ; units walked: pose of the walk {2}
hacc    ds 1            ; fraction of a step: sideways, {2}
vacc    ds 1            ; up and down {2}
thrust  ds 1            ; frames of the thrust still to go {2}
parry   ds 1            ; frames of the parry still to {6}
                        ; go (things.asm starts it) {6}
moved   ds 1            ; he moved in this frame {2}
swx     ds 1            ; the blade: column, NUSIZ0, RESMP0 {2}
swnus   ds 1 ; {2}
swres   ds 1 ; {2}
; == player 1, the plug (main.asm: setup_room, {4}
; == p1_bands: the thing of band A) {4}
;|; == the plug (main.asm: setup_room) {3-3}
ox      ds 1            ; column {4}
oy      ds 1            ; top line (odd) {4}
odir    ds 1            ; 0 right, 8 left (REFP1) {4}
okind   ds 1            ; first frame in the OG tables {4}
onus    ds 1            ; NUSIZ1 in the room {4}
plug    ds 1            ; ENABL in the room: 2 the ball {3}
; == the things (things.asm; new_game and setup_room {4}
; == start them) {4}
key     ds 1            ; the key he has: its level, 0 none {4}
opened  ds 1            ; open: chests bits 0-3, doors 4-7 {4}
spk     ds 1            ; frames left before the plates turn {4}
spup    ds 1            ; the plates: 0 down, 1 up {4}
hurt    ds 1            ; frames before a wound can come {5}
                        ; again (the spikes, a bite) {5}
; == the collision test (knight.asm: box_free, wall) {2}
cmap    ds 2            ; collision map of the room {2}
                        ; (main.asm: room_state) {2}
nx      ds 1            ; the box tried: column, top line {2}
ny      ds 1 ; {2}
bc0     ds 1            ; its block columns, left, right {2}
bc1     ds 1 ; {2}
br      ds 1            ; 3 x the block row tested (its {2}
                        ; first byte in the map) {2}
; == sound (sound.asm; mode: main.asm, SELECT on the title; {8}
;|; == sound (sound.asm; mode: main.asm, SELECT; {7-7}
; == sfxreq: knight.asm asks, sound.asm clears; song: {7}
; == main.asm and things.asm) {7}
mode    ds 1            ; 0 MUSIC, 1 SOUND FX, 2 SILENT {7}
smode   ds 1            ; the mode the player last saw ($FF: {7}
                        ; a song to start) {7}
song    ds 1            ; 2 x the song (main.asm, {7}
                        ; things.asm choose it) {7}
sfxreq  ds 1            ; effect asked for (0: none) {7}
sfxi    ds 1            ; effect playing: its frame, 0 none {7}
mclock  ds 1            ; frames left in this step {7}
mstep   ds 1            ; index in STEPLEN {7}
vpos    ds 2            ; each voice: offset in its stream, {7}
vleft   ds 2            ; steps left of its note, {7}
venv    ds 2            ; frame of the note (envelope), {7}
vins    ds 2            ; instrument, {7}
vnote   ds 2            ; note (0: a rest) {7}
; == the seam of player 1 (main.asm prepares; {5}
; == room_kernel.asm) {5}
zcnt    ds 1            ; courses to the seam (0: none) {5}
zcoarse ds 1            ; the delay before RESP1 there {5}
zref    ds 1            ; REFP1 below the seam {5}
s2gfx   ds 2            ; player 1 below the seam: graphics, {5}
s2col   ds 2            ; colours {5}
; == GAME OVER, VICTORY (things.asm sets them, main.asm {8}
; == counts) {8}
;|; == GAME OVER, VICTORY (things.asm sets them) {5-7}
over    ds 1            ; 0 playing, else 1 + frames since {8}
                        ; it began, up to GO_FRAMES {8}
;|over    ds 1            ; 0 playing, 1 GAME OVER {5-7}
won     ds 1            ; the same for VICTORY, up to {8}
                        ; VIC_FRAMES {8}
;|won     ds 1            ; 0 playing, 1 VICTORY {6-7}
; == the kernels (main.asm prepares; room_kernel.asm)
kgfx    ds 2            ; Sir Roderick: graphics, colours
kcol    ds 2
sgfx    ds 2            ; player 1: graphics, colours {4}
scol    ds 2 ; {4}
cbk     ds 2            ; room colours: COLUBK, COLUPF
cpf     ds 2
zbk     ds 1            ; COLUBK of the next line A
zt      ds 1            ; colour for Y at the end of a line
zc1     ds 1            ; COLUP1 of the next line B {4}
idx     ds 1            ; index of the line being prepared
trow    ds 1            ; Superchip index of the next course
znpf0   ds 1            ; PF0, PF1, PF2 of the next course
znpf1   ds 1
znpf2   ds 1
; == the HUD (main.asm prepares; hud.asm) {3}
dig     ds 12           ; the six columns of digits {3}
txp     ds 12           ; and of the name of the level {3}
zt2     ds 1 ; {3}
bar1    ds 1            ; energy bar: PF1, PF2 {3}
bar2    ds 1 ; {3}
; == scratch (anyone; never kept across a call; the room {5}
; == kernel keeps a value of the seam in tmp) {5}
;|; == scratch (anyone; never kept across a call) {1-4}
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

;|; A bank whose code comes in a later step has only its {1-7}
;|; tail, and the routine its trampoline goes to is a stub: {1-7}
;|; never called before that step. {1-7}

; --- bank 0: the room -------------------------------------
        BANK    0
        include "kfig0.asm"
        include "room_kernel.asm"
        include "bank0.asm"
bank0_end
        TAIL    0

; --- bank 1: title ----------------------------------------
        BANK    1
        include "title_kernel.asm" ; {8}
        include "bank1.asm" ; {8}
;|title_kernel:                  ; (step 8) {1-7}
;|        jmp     TO_MAIN {1-7}
bank1_end
        TAIL    1

; --- bank 2: the throne room ------------------------------
        BANK    2
        include "kfig2.asm" ; {6}
        ; Sir Roderick at the same place as in bank 0 {6}
        IF KFG_2-$4000 != KFG || KFG_END_2-$4000 != KFG_END ; {6}
        ERR ; {6}
        ENDIF ; {6}
        include "throne_kernel.asm" ; {6}
        include "bank2.asm" ; {6}
;|throne_kernel:                 ; (step 6) {1-5}
;|        jmp     TO_MAIN {1-5}
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
        include "things.asm" ; {4}
        include "bank4.asm" ; {4}
;|things:                        ; (step 4) {1-3}
;|        rts {1-3}
bank4_end
        TAIL    4
; --- bank 5: sound ---------------------------------------
        BANK    5
        include "sound.asm" ; {7}
        include "bank5.asm" ; {7}
;|sound:                         ; (step 7) {1-6}
;|        rts {1-6}
bank5_end
        TAIL    5
; --- bank 6: the end screens ----------------------------
        BANK    6
        include "ends_kernel.asm" ; {8}
        include "bank6.asm" ; {8}
;|ends_kernel:                   ; (step 8) {1-7}
;|        jmp     TO_MAIN {1-7}
bank6_end
        TAIL    6

; --- bank 7: start, frame, logic, HUD ---------------------
        BANK    7
        include "main.asm"
        include "knight.asm" ; {2}
        include "hud.asm"
        include "bank7.asm"
bank7_end
        TAIL    7
