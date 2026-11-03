# Experiment 7x: A hiss left on

Chapter 13, "Effects and sound modes", prints this experiment and explains it: a "Where it breaks" version. This folder is step 07 (`chain/07-sound`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/sound.asm`, the line

```text
ef_end: lda     #0
```

becomes

```text
ef_end: rts
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 07, with the same inputs (the head of the step's route, 857 frames on NTSC from bank 0), in the simulator: 262 lines; sfxi from frame 224; the sound. It passed, as a "Where it breaks" version: it breaks what the chapter says it breaks. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/7x.json`.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `84eb9179d95ffa9a345b0cb3280adfa2ec1cfca4b91c3ee2825758c3646dcdb7` |
| `game/build/scalecrown_pal.bin` | `5d6c04f33bc6f207d659cebd4c55f3663011ac9c82cbec6beb15b30cc61a353d` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/07-sound`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
