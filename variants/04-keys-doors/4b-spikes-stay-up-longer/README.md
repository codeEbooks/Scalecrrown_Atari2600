# Experiment 4b: The spikes stay up longer

Chapter 7, "Keys, doors and treasure", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 04 (`chain/04-keys-doors`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
SPIKES_UP_S = 1.0
```

becomes

```text
SPIKES_UP_S = 2.0
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 04, with the same inputs (the head of the step's route, 411 frames on NTSC from bank 0), in the simulator: 262 lines; spk from frame 229. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/4b.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `3b1f77a11fd304d793933c19284cd751ef78050f3debd9415ad6bcf75c298b2e` |
| `game/build/scalecrown_pal.bin` | `c4c0e1f27860229e3fbd548d417898361e7d9b60e6eb69387edd38cc873eced1` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/04-keys-doors`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
