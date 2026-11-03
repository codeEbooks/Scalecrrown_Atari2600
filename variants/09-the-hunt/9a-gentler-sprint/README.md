# Experiment 9a: A gentler sprint

Chapter 15, "The hunt: how hard the game is", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 09 (`chain/09-the-hunt`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
SPRINT_PX_S = {1: 50, 2: 52, 3: 54, 4: 56}
```

becomes

```text
SPRINT_PX_S = {1: 40, 2: 44, 3: 48, 4: 50}
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 09, with the same inputs (the head of the step's route, 977 frames on NTSC from bank 0), in the simulator: 262 lines; SC_SPR from frame 131. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/9a.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `57ff86b9b0c829b661f9ff36517f5ba41a7574def4651e8e25668f77fe04709e` |
| `game/build/scalecrown_pal.bin` | `7428ef6fbac6a9967b418879e1cabe93d49714b18c214d38609a1a0b44fab11f` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/09-the-hunt`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
