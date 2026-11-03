# Scalecrown, step 4 of 9: keys and doors

Player 1 shows the thing of the room: a chest in each level (it
opens, Sir Roderick has the key of the level), the golden gate
before the throne room. The doors are closed: the grate on the
stair down of levels 1-3 and the gate open with the key. The
plates of the spikes go up and down. Points for chests and doors.

## What this step adds

- `things.asm` (bank 4, through TO_THINGS in the overscan): the
  plates, what Sir Roderick touches, the points.
- `room_kernel.asm`: player 1 in every line (GRP1, COLUP1, its
  pointers). The lines are fuller: PF2 moves from line A0 to the
  end of line B3 (cycle 61, after the right half is drawn).
- `hud.asm`: line 27 puts player 1 at its column.
- `main.asm`: `p1_bands` (the thing of the room, or the empty
  figure), `room_state` (the thing open or closed, the map with
  the door closed, the key in the HUD).

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

Step 5 brings the serpents and the seam.
