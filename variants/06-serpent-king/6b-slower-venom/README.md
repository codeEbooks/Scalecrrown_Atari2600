# Experiment 6b: Slower venom

Chapter 11, "The Serpent King", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 06 (`chain/06-serpent-king`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
VENOM_PX_S = 112         # easier: 90
```

becomes

```text
VENOM_PX_S = 90          # easier: 90
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 06, with the same inputs (the head of the step's route, 11 746 frames on NTSC from bank 0), in the simulator: 262 lines; SC_VA from frame 11 698. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/6b.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `1028180b70d3293d47091fd2d818f9b51d4323bfa291c4311b081f09e5df876e` |
| `game/build/scalecrown_pal.bin` | `f75241d0b82bbaf0baec319d04df889f4768c54f7848f73aae51381dce269a74` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/06-serpent-king`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
