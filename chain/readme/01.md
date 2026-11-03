# Scalecrown, step 1 of 9: the first room

The cartridge starts, clears the RAM and draws the room where Sir
Roderick comes into the Crypt of Scales, The Broken Gate, with
him standing at the place where he comes in. Nothing moves yet.

## What this step has

- `scalecrown.asm`: the eight banks of the F4 cartridge, each one
  with the 256 bytes of the Superchip window and the same tail:
  every trampoline of the finished game (to the room kernel, the
  copy of a room, back to the frame; to the title, the throne
  room, the end screens, the things and the sound too). The banks
  that come later have only their tail, and the routine their
  trampoline goes to is a stub that nothing calls yet.
- `main.asm` (bank 7): the start, the frame (VSYNC, the VBLANK
  timer, the overscan timer), `new_game`, `setup_room` (the copy
  of the room into the Superchip RAM, through bank 3) and
  `prep_room` (the pointers of Sir Roderick and of the colours).
- `hud.asm`: no HUD yet: 26 black lines, then line 26 puts Sir
  Roderick at his column and line 28 moves him (HMOVE).
- `room_kernel.asm` (bank 0): 160 lines in 20 courses of 8 lines,
  lines A and B in turn. One figure, Sir Roderick (player 0), and
  the playfield: line A0 of each course writes PF0, PF1 and PF2
  (cycles 17, 23, 29); the colours come from two tables read
  through pointers.
- `dungeon.asm` (bank 3): `room_copy`, 60 bytes unrolled.
- `game/assets`: the plan of the whole crypt (dungeon.py,
  rooms.py), the look (look.py, art.py), the rules (rules.py);
  `build_assets.py` writes only the data this step reads.

## Build it and run it

    python3 tools/build.py

needs Python 3.10 or later and dasm 2.20.14.1 (on the PATH, or
`--dasm PATH`). It writes `game/build/scalecrown_ntsc.bin` and
`scalecrown_pal.bin` (32K, F4 with the Superchip), their
listings and symbols, and `game/build/manifest.json` (the bytes
free in each bank). Open a cartridge in Stella 7.0.

Every step is cut from the same source, the finished game:
the files of this folder are the files of the game with the
lines of the later steps taken out.

Step 2 gives Sir Roderick the joystick and the sword.
