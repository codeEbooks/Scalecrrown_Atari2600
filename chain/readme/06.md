# Scalecrown, step 6 of 9: the Serpent King

The throne room has its own kernel, in bank 2: the Serpent King,
twice as wide, goes up and down to meet Sir Roderick and spits
venom (missile 1); the oak shield parries what comes from the
side Sir Roderick faces. Ten blows beat the King; the crown
appears on the throne; struck, it breaks: VICTORY, and the game
stops.

## What this step adds

- `throne_kernel.asm` (bank 2) and `kfig2.asm`: the same figures
  of Sir Roderick at the same place as in bank 0.
- `things.asm`: `throne` (the blows, the bite, the venom, the
  steps, the spit), `blade_on`.
- `main.asm`: `p1_throne`, the venom's column; `knight.asm`: the
  parry.

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

Step 7 adds the sound.
