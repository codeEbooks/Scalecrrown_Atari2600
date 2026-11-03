# Scalecrown, step 3 of 9: the dungeon

The sixteen rooms in four levels: through the openings east and
west Sir Roderick goes to the room beside, by the stairs to the
level below and back; the ball (the plug) closes the outer
opening of the rooms at the ends of a level. Each level has its
colours; the torches flicker; in level 3 the water shimmers. The
HUD shows the score, the energy and the name of the level. The
doors are open in this step: the keys come in step 4.

## What this step adds

- `knight.asm`: the rooms east and west, the stairs.
- `hud.asm`: the HUD, two 48-pixel routines (the six digits, LEVEL
  n) with both players delayed, and the energy bar in the
  playfield.
- `main.asm`: the name of the level, the plug, the torches, the
  water; the HUD's positions (HMOVE and HMCLR in `prep_room`).
- `dungeon.asm`: after the copy, the bytes of the open door.
- `room_kernel.asm`: the ball on in the room, off after it.

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

Step 4 puts player 1 in the kernel: chests, keys and doors.
