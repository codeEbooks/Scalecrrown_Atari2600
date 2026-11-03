# Experiment 6a: Five blows beat the King

Chapter 11, "The Serpent King", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 06 (`chain/06-serpent-king`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
KING_HITS = 10          # blows of the sword to beat him
```

becomes

```text
KING_HITS = 5           # blows of the sword to beat him
```

In `game/assets/rules.py`, the line

```text
SPIT_S = (1.6, 1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7)
```

becomes

```text
SPIT_S = (1.6, 1.4, 1.2, 1.0, 0.8)
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 06, with the same inputs (the head of the step's route, 12 175 frames on NTSC from bank 0), in the simulator: 262 lines; SC_KS from frame 11 909. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/6a.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `6636f1812919109e5151244fb590bf7db223fe36dff6111ea1e4e586773224f7` |
| `game/build/scalecrown_pal.bin` | `8e9ae59ed8daf63d3c1a31aded486c12f0525d606d5033f293068a0b091ad486` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/06-serpent-king`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
