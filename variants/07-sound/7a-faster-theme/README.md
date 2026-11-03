# Experiment 7a: A faster theme

Chapter 12, "The TIA and the music", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 07 (`chain/07-sound`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/score.py`, the line

```text
BPM = 100
```

becomes

```text
BPM = 140
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 07, with the same inputs (the head of the step's route, 12 339 frames on NTSC from bank 0), in the simulator: 262 lines; mclock from frame 1; the sound. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/7a.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `9c0324fc0ee32d19f677c9dcc9e416891e70f92ba60b41ed38f2d7f80c90b022` |
| `game/build/scalecrown_pal.bin` | `8a5131b641715590f859fe95ef33c862a7fbcd9d23a9d7b6c772e6dd99556a47` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/07-sound`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
