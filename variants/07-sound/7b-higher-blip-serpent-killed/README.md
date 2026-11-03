# Experiment 7b: A higher blip for a serpent killed

Chapter 13, "Effects and sound modes", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 07 (`chain/07-sound`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/sfx.py`, the line

```text
    "kill": [(12, 16, 12), (12, 13, 12), (12, 10, 11),
```

becomes

```text
    "kill": [(12, 12, 12), (12, 9, 12), (12, 6, 11),
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 07, with the same inputs (the head of the step's route, 357 frames on NTSC from bank 0), in the simulator: 262 lines; the RAM the same; the sound. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/7b.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `660ba71b96af3fdd13f0aaf363764f848c66f714618100a1a1a146f17fa9acbf` |
| `game/build/scalecrown_pal.bin` | `e7a5e9a422110552f797af4ba673cb7dfb641b555a384d1ef582fa73d41819c6` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/07-sound`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
