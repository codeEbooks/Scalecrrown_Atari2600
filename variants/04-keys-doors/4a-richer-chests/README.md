# Experiment 4a: Richer chests

Chapter 7, "Keys, doors and treasure", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 04 (`chain/04-keys-doors`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
CHEST_POINTS = 500
```

becomes

```text
CHEST_POINTS = 1500
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 04, with the same inputs (the head of the step's route, 983 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; score+1 from frame 949; 1 of 5 pictures. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/4a.json`. `evidence/4a_step.png` and `evidence/4a_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `50e8f7203bacb8561e09dc556b86f8f341a25a67651e3261168b8655505db30e` |
| `game/build/scalecrown_pal.bin` | `212a2f963be9c700ebe3370df6f972b67724d34ef59ea6cec0db0b792754c2a6` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/04-keys-doors`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
