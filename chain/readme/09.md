# Scalecrown, step 9 of 9: the hunt

The finished game, Scalecrown 1.0, byte for byte. A serpent on
Sir Roderick's lines chases him along its path, sprinting; it
takes two blows (the first pushes it back, stuns it and makes it
blink) and comes back a while after it dies. The Serpent King is
struck only on its head, where the venom flies. These are the
last changes made to the game, to make it harder: chapter 15
shows how the difficulty is set.

## Build it and run it

    python3 tools/build.py

needs Python 3.10 or later and dasm 2.20.14.1 (on the PATH, or
`--dasm PATH`). It writes `game/build/scalecrown_ntsc.bin` and
`scalecrown_pal.bin` (32K, F4 with the Superchip), their
listings and symbols, and `game/build/manifest.json` (the bytes
free in each bank). Open a cartridge in Stella 7.0.

The two cartridges of this step are those of Scalecrown
1.0, byte for byte.

Every step is cut from the same source, the finished game:
the files of this folder are the files of the game with the
lines of the later steps taken out.
