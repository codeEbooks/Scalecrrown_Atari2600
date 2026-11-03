# Scalecrown, step 2 of 9: Sir Roderick

The joystick moves Sir Roderick through the room, the walls stop
him (he slides along a wall when pushed diagonally into it), the
button thrusts the sword: the blade is missile 0. RESET starts
again. The edges of the screen stop him: the other rooms come in
step 3.

## What this step adds

- `knight.asm`: his frame: the thrust, the walk (a fraction of a
  pixel a frame, from a table for each television), the poses of
  the walk, `box_free` and `wall` on the collision map of the
  room, `blade` (where missile 0 goes, and how wide).
- `main.asm`: `buttons` (fire, RESET), RESET in the frame,
  `room_state` (the collision map), `place` (an object to its
  column; its loop kept in one page), the position of the blade.
  The HMOVE of HUD line 28 moves the blade with Sir Roderick.
- `room_kernel.asm`: lines B write his colour to ENAM0 too (cycle
  8): bit 1 of it switches the blade.

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

Step 3 opens the openings and the stairs: the sixteen rooms.
