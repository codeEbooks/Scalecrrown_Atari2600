# Experiment 8b: A longer GAME OVER

Chapter 14, "States, title and end screens", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 08 (`chain/08-title-and-ends`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
GAME_OVER_S = 1.0
```

becomes

```text
GAME_OVER_S = 2.0
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 08, with the same inputs (the head of the step's route, 13 711 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; screen from frame 13 679; 1 of 56 pictures. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/8b.json`. `evidence/8b_step.png` and `evidence/8b_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `f5c35c1499978a1def0d57653fa53f8d605b7122bb2b59ed58e3b628b46b01af` |
| `game/build/scalecrown_pal.bin` | `ca1cbf0f262582567c74573293cf3835eb759178c094b26126bcd07e10dfa233` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/08-title-and-ends`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
