# Experiment 9b: They come back sooner

Chapter 15, "The hunt: how hard the game is", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 09 (`chain/09-the-hunt`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
RESPAWN_S = 4.0
```

becomes

```text
RESPAWN_S = 2.0
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 09, with the same inputs (the head of the step's route, 1 217 frames on NTSC from bank 0), in the simulator: 262 lines; SC_GT from frame 945. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/9b.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `b3589d5adcd24d679806c249943c2994361f66432ae834b64b5149bd1bf4cf03` |
| `game/build/scalecrown_pal.bin` | `d22a161baa6e6ee299ea8099aa69d62b3e55a76266f7a4e6dbb6a9788d0bc8b3` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/09-the-hunt`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
