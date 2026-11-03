# Experiment 9x: A serpent that never comes back

Chapter 15, "The hunt: how hard the game is", prints this experiment and explains it: a "Where it breaks" version. This folder is step 09 (`chain/09-the-hunt`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/things.asm`, the line

```text
        jsr     respawn
```

is taken out.

## What its test saw

`tools/make_variants.py` built it and played it beside step 09, with the same inputs (the head of the step's route, 1 217 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; zcoarse from frame 1 185; 1 of 21 pictures. It passed, as a "Where it breaks" version: it breaks what the chapter says it breaks. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/9x.json`. `evidence/9x_step.png` and `evidence/9x_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `980ad1b6833dcccc1550b97c2343e73b2e9150033d542db40b14b86547ae5fd6` |
| `game/build/scalecrown_pal.bin` | `014480d87bae143123c490d428b0e35fbf330c1b721b65910e418cb888347788` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/09-the-hunt`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
