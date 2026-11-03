# Experiment 2b: A longer thrust

Chapter 5, "The knight", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 02 (`chain/02-knight`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
THRUST_S = 0.2          # the thrust of the sword, seconds
```

becomes

```text
THRUST_S = 0.4          # the thrust of the sword, seconds
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 02, with the same inputs (the head of the step's route, 204 frames on NTSC from bank 0), in the simulator: 262 lines; thrust from frame 171. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/2b.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `483e438b088663c12b63028c77d8a214a6050bb2446adf19d269d56eb4f614dd` |
| `game/build/scalecrown_pal.bin` | `583d82226d81a2b7d888a702fe7c34325bae4441af6681b52e6424f0910e9202` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/02-knight`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
