# Scalecrown, step 8 of 9: the title and the end screens

The title (bank 1) with its decor and the three modes of sound,
chosen with SELECT; the button or RESET starts a game. After GAME
OVER or VICTORY the end screen (bank 6) with the score, the
lament or the fanfare; the button goes back to the title. The
whole game, but for the hunt of step 9: the serpents only crawl
to and fro, one blow kills them and they come back only when Sir
Roderick comes into their room again, the King is struck
anywhere on his body.

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

Step 9, the last, is the hunt.
