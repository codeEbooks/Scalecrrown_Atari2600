# Experiment 2a: A faster walk

Chapter 5, "The knight", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 02 (`chain/02-knight`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
WALK_PX_S = 60          # pixels a second, left and right
```

becomes

```text
WALK_PX_S = 90          # pixels a second, left and right
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 02, with the same inputs (the head of the step's route, 204 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; hacc from frame 46; 3 of 4 pictures. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/2a.json`. `evidence/2a_step.png` and `evidence/2a_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `53c22baee85be05fa632a9eb8a41a554c2d5d7c77cd8dcd4a347c2ad314a1426` |
| `game/build/scalecrown_pal.bin` | `b0c61a9ebb5c3b32c3aba0de9d01d3a69dae9d656169b07b421b66801559e9cf` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/02-knight`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
