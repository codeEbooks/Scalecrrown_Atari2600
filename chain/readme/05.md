# Scalecrown, step 5 of 9: the serpents

Two serpents in each of thirteen rooms crawl to and fro, faster
in the lower levels. A bite takes energy, and so do the raised spikes;
a wound makes Sir Roderick flash. A thrust of the sword kills a
serpent (it is back when he comes in again). Energy 0: GAME OVER,
and the game stops; RESET starts again. Two things on player 1:
the kernel moves it, in the middle of the room, to the serpent
of the band below (the seam); two things in the same lines take
turns (the flicker).

## What this step adds

- `things.asm`: `guards`, `guard` (the blade, the bite, the
  crawl), `wound`, GAME OVER.
- `room_kernel.asm`: the seam (`k_seam`): six lines that move
  player 1 (RESP1 after a delay, then HMOVE).
- `main.asm`: `p1_bands` with the two bands and the flicker; the
  flash.

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

Step 6 opens the throne room.
