# Scalecrown, step 7 of 9: the sound

The sound player of bank 5: the theme on both voices, or the
effects (the sword, the stairs, the chest, the door, the bites,
the blows), or silence. In this step SELECT, in the game, chooses
MUSIC, SOUND FX or SILENT.

## What this step adds

- `sound.asm` (bank 5, through TO_SOUND in the overscan) and the
  tables of `music.py`, `score.py`, `sfx.py`.
- the requests of the effects (`sfxreq`) in `knight.asm` and
  `things.asm`; `theme` in `main.asm`.

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

Step 8 adds the title and the end screens.
