# Experiment 5b: A softer bite

Chapter 9, "The sword and the damage", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 05 (`chain/05-serpents`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rules.py`, the line

```text
BITE_DAMAGE = 3          # easier: 2
```

becomes

```text
BITE_DAMAGE = 1          # easier: 2
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 05, with the same inputs (the head of the step's route, 220 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; energy from frame 188; 2 of 3 pictures. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/5b.json`. `evidence/5b_step.png` and `evidence/5b_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `99ea3888f552365dfa2faa3657d12dc548275b3957ae0729c7d7005fb6c6eb6c` |
| `game/build/scalecrown_pal.bin` | `b319ecdcb199bd55e3e5cd29128bf7e2e8b396ceff6acfefff667e7b88209e6c` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/05-serpents`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
