# Experiment 5a: Slower serpents in the first level

Chapter 8, "The serpents", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 05 (`chain/05-serpents`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
SERPENT_PX_S = {1: 38, 2: 42, 3: 46, 4: 49}
```

becomes

```text
SERPENT_PX_S = {1: 20, 2: 42, 3: 46, 4: 49}
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 05, with the same inputs (the head of the step's route, 220 frames on NTSC from bank 0), in the simulator: 262 lines; SC_ACC from frame 1. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/5a.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `79f7e35d12d27f9d67ddc61b7cb9c9030e6a944a6f0745b16cd79a0b45078ba0` |
| `game/build/scalecrown_pal.bin` | `333cb27b43125d7d7a35d925306830074c35a90031e1923974d54007761bbf1b` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/05-serpents`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
