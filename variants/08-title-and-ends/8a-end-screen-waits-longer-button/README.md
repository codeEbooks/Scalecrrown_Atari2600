# Experiment 8a: The end screen waits longer for the button

Chapter 14, "States, title and end screens", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 08 (`chain/08-title-and-ends`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
END_S = 1.0
```

becomes

```text
END_S = 2.0
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 08, with the same inputs (the head of the step's route, 13 034 frames on NTSC from bank 0), in the simulator: 262 lines; won from frame 12 996. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/8a.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `cdabfe651da2a8a3ac76c07e6e9f2fadf19a9c4521553328c65504a93e453904` |
| `game/build/scalecrown_pal.bin` | `df00275b5336e4c72239498956162250639321508485cee4bb4f7036e8acc3c1` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/08-title-and-ends`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
