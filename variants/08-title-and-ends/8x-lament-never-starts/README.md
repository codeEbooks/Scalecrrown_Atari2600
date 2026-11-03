# Experiment 8x: The lament never starts

Chapter 14, "States, title and end screens", prints this experiment and explains it: a "Where it breaks" version. This folder is step 08 (`chain/08-title-and-ends`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/things.asm`, the line

```text
        sta     smode           ; silences what played)
```

is taken out.

## What its test saw

`tools/make_variants.py` built it and played it beside step 08, with the same inputs (the head of the step's route, 13 711 frames on NTSC from bank 0), in the simulator: 262 lines; vpos from frame 13 619; the sound. It passed, as a "Where it breaks" version: it breaks what the chapter says it breaks. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/8x.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `0b2c9df4a9b29fa8d180994ac8e1c2aa7803955595c5ffe0a632723d1d4c6f84` |
| `game/build/scalecrown_pal.bin` | `84b8ea108715a6de08709e7ca7afdd5f9efe5f82deee081fee6137d08735cfae` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/08-title-and-ends`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
