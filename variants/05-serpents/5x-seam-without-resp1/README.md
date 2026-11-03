# Experiment 5x: The seam without RESP1

Chapter 8, "The serpents", prints this experiment and explains it: a "Where it breaks" version. This folder is step 05 (`chain/05-serpents`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/room_kernel.asm`, the line

```text
        sta     RESP1           ; 19 + 5 x zcoarse (24-69)
```

is taken out.

## What its test saw

`tools/make_variants.py` built it and played it beside step 05, with the same inputs (the head of the step's route, 223 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; the RAM the same; the seam wrong; 2 of 3 pictures. It passed, as a "Where it breaks" version: it breaks what the chapter says it breaks. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/5x.json`. `evidence/5x_step.png` and `evidence/5x_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `02245ddba5f131d0ba4fd10ddaec03570349af067320a9cab406fa998723f052` |
| `game/build/scalecrown_pal.bin` | `049bd8410d3ad3cfe6f1bc6e81643ae3eecbd3d8874dcdc33ec9792a7e79213f` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/05-serpents`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
