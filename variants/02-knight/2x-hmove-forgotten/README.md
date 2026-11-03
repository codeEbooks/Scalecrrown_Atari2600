# Experiment 2x: The HMOVE forgotten

Chapter 5, "The knight", prints this experiment and explains it: a "Where it breaks" version. This folder is step 02 (`chain/02-knight`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/hud.asm`, the line

```text
        sta     HMOVE           ;  2
```

is taken out.

## What its test saw

`tools/make_variants.py` built it and played it beside step 02, with the same inputs (the head of the step's route, 190 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; the RAM the same; 3 of 3 pictures. It passed, as a "Where it breaks" version: it breaks what the chapter says it breaks. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/2x.json`. `evidence/2x_step.png` and `evidence/2x_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `bb60380bf2f06a31057535f64dffc50613e2f1a09b43c25da309a6225cf11e50` |
| `game/build/scalecrown_pal.bin` | `1ff67959055eccebb90fc6dc910b9577e9bc61f671e749e577483ac526bc75ab` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/02-knight`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
