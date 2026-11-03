# The chapters and their folders

The book builds the game in nine steps. Each chapter works on a step of
`chain/`; its experiments are in `variants/`, in the folder of the same
step. An experiment is the step with one change: a guided variant
("Make it yours") shows what a value or a line does, a "Where it
breaks" version makes on purpose a mistake the chapter explains.

| Chapter | Title | Step | Experiments | Tools and tests it names |
|---|---|---|---|---|
| 1 | Your workshop | `chain/01-first-room` |  | `tools/build.py` |
| 2 | The 6507, the memory and the cartridge | `chain/01-first-room` | `1b-sir-roderick-comes-in-further-west` |  |
| 3 | Racing the beam: the frame | `chain/01-first-room` | `1x-wsync-forgotten` |  |
| 4 | The playfield and the first room | `chain/01-first-room` | `1a-upper-crypt-in-blue` | `tools/build.py` |
| 5 | The knight | `chain/02-knight` | `2a-faster-walk`, `2b-longer-thrust`, `2x-hmove-forgotten` | `tools/build.py` |
| 6 | The dungeon and the HUD | `chain/03-dungeon` | `3a-water-shimmers-twice-as-fast`, `3b-red-score`, `3x-row-two-cycles-early` | `tools/build.py` |
| 7 | Keys, doors and treasure | `chain/04-keys-doors` | `4a-richer-chests`, `4b-spikes-stay-up-longer`, `4x-pf2-never-written-in-room` | `tools/build.py` |
| 8 | The serpents | `chain/05-serpents` | `5a-slower-serpents-in-first-level`, `5x-seam-without-resp1` | `tools/build.py` |
| 9 | The sword and the damage | `chain/05-serpents` | `5b-softer-bite` |  |
| 10 | The throne room | `chain/06-serpent-king` | `6x-venom-never-switched-on` | `tools/build.py` |
| 11 | The Serpent King | `chain/06-serpent-king` | `6a-five-blows-beat-king`, `6b-slower-venom` |  |
| 12 | The TIA and the music | `chain/07-sound` | `7a-faster-theme` | `tools/build.py` |
| 13 | Effects and sound modes | `chain/07-sound` | `7b-higher-blip-serpent-killed`, `7x-hiss-left-on` |  |
| 14 | States, title and end screens | `chain/08-title-and-ends` | `8a-end-screen-waits-longer-button`, `8b-longer-game-over`, `8x-lament-never-starts` | `tools/build.py` |
| 15 | The hunt: how hard the game is | `chain/09-the-hunt` | `9a-gentler-sprint`, `9b-they-come-back-sooner`, `9x-serpent-that-never-comes-back` | `tests/verify_0_9.py`, `tools/build.py` |
| 16 | Reading and checking the game | `chain/09-the-hunt`, `game` |  | `tests/coverage_notes.py`, `tests/model.py`, `tests/sound_model.py`, `tests/stella_run.py`, `tests/tia_audio.py`, `tests/vcs_sim.py`, `tests/verify_0_9.py`, `tools/build.py` |
| 17 | Glossary and index |  |  |  |

Step 09 is the complete game, Scalecrown 1.0, byte for byte; `game/`
holds its master source, from which `tools/make_chain.py` makes the nine
steps.

## The experiments

| Folder | Chapter | Kind | Title | What its test saw |
|---|---|---|---|---|
| `variants/01-first-room/1a-upper-crypt-in-blue` | 4 | variant | The Upper Crypt in blue | 262 lines; the RAM the same; 2 of 2 pictures |
| `variants/01-first-room/1b-sir-roderick-comes-in-further-west` | 2 | variant | Sir Roderick comes in further west | 262 lines; `kx` from frame 1; 2 of 2 pictures |
| `variants/01-first-room/1x-wsync-forgotten` | 3 | where it breaks | A WSYNC forgotten | 261 lines; 2 of 2 pictures |
| `variants/02-knight/2a-faster-walk` | 5 | variant | A faster walk | 262 lines; `hacc` from frame 46; 3 of 4 pictures |
| `variants/02-knight/2b-longer-thrust` | 5 | variant | A longer thrust | 262 lines; `thrust` from frame 171 |
| `variants/02-knight/2x-hmove-forgotten` | 5 | where it breaks | The HMOVE forgotten | 262 lines; the RAM the same; 3 of 3 pictures |
| `variants/03-dungeon/3a-water-shimmers-twice-as-fast` | 6 | variant | The water shimmers twice as fast | 262 lines; the RAM the same; 1 of 22 pictures |
| `variants/03-dungeon/3b-red-score` | 6 | variant | A red score | 262 lines; the RAM the same; 12 of 12 pictures |
| `variants/03-dungeon/3x-row-two-cycles-early` | 6 | where it breaks | The row two cycles early | 262 lines; the RAM the same; 12 of 12 pictures |
| `variants/04-keys-doors/4a-richer-chests` | 7 | variant | Richer chests | 262 lines; `score+1` from frame 949; 1 of 5 pictures |
| `variants/04-keys-doors/4b-spikes-stay-up-longer` | 7 | variant | The spikes stay up longer | 262 lines; `spk` from frame 229 |
| `variants/04-keys-doors/4x-pf2-never-written-in-room` | 7 | where it breaks | PF2 never written in the room | 262 lines; the RAM the same; 5 of 5 pictures |
| `variants/05-serpents/5a-slower-serpents-in-first-level` | 8 | variant | Slower serpents in the first level | 262 lines; `SC_ACC` from frame 1 |
| `variants/05-serpents/5b-softer-bite` | 9 | variant | A softer bite | 262 lines; `energy` from frame 188; 2 of 3 pictures |
| `variants/05-serpents/5x-seam-without-resp1` | 8 | where it breaks | The seam without RESP1 | 262 lines; the RAM the same; the seam wrong; 2 of 3 pictures |
| `variants/06-serpent-king/6a-five-blows-beat-king` | 11 | variant | Five blows beat the King | 262 lines; `SC_KS` from frame 11 909 |
| `variants/06-serpent-king/6b-slower-venom` | 11 | variant | Slower venom | 262 lines; `SC_VA` from frame 11 698 |
| `variants/06-serpent-king/6x-venom-never-switched-on` | 10 | where it breaks | The venom never switched on | 262 lines; the RAM the same; 1 of 29 pictures |
| `variants/07-sound/7a-faster-theme` | 12 | variant | A faster theme | 262 lines; `mclock` from frame 1; the sound |
| `variants/07-sound/7b-higher-blip-serpent-killed` | 13 | variant | A higher blip for a serpent killed | 262 lines; the RAM the same; the sound |
| `variants/07-sound/7x-hiss-left-on` | 13 | where it breaks | A hiss left on | 262 lines; `sfxi` from frame 224; the sound |
| `variants/08-title-and-ends/8a-end-screen-waits-longer-button` | 14 | variant | The end screen waits longer for the button | 262 lines; `won` from frame 12 996 |
| `variants/08-title-and-ends/8b-longer-game-over` | 14 | variant | A longer GAME OVER | 262 lines; `screen` from frame 13 679; 1 of 56 pictures |
| `variants/08-title-and-ends/8x-lament-never-starts` | 14 | where it breaks | The lament never starts | 262 lines; `vpos` from frame 13 619; the sound |
| `variants/09-the-hunt/9a-gentler-sprint` | 15 | variant | A gentler sprint | 262 lines; `SC_SPR` from frame 131 |
| `variants/09-the-hunt/9b-they-come-back-sooner` | 15 | variant | They come back sooner | 262 lines; `SC_GT` from frame 945 |
| `variants/09-the-hunt/9x-serpent-that-never-comes-back` | 15 | where it breaks | A serpent that never comes back | 262 lines; `zcoarse` from frame 1 185; 1 of 21 pictures |

"Its test" is what `tools/make_variants.py` found when it built the
experiment and played it beside its step (chapter 16, Table 16.9): a
variant passes when it keeps the time of every frame and changes what
it says it changes; a "Where it breaks" version passes when it breaks
what the chapter says it breaks. Every folder has a README: the change,
the lines before and after, what the test saw, and how to go back to
the step.

## The tools

| File | What it does |
|---|---|
| `tools/build.py` | Builds the complete game in `game/`, from the master source; every step and experiment has its own copy, which builds its folder (chapter 1) |
| `tools/make_chain.py` | Makes the nine steps of `chain/` from the master source and its step tags; `--assemble` also builds them, writes `chain/chain.json` and checks that step 09 is the release |
| `tools/variants.py` | The 27 changes of the experiments, and what each one claims |
| `tools/make_variants.py` | Makes each experiment from its step in a temporary folder, builds it and plays it beside the step, in the simulator (and in Stella for the pictures), and checks what it claims |
| `tools/chain_figures.py`, `tools/figure_list.py` | The 46 figures of the book taken from the steps: each frame captured twice in Stella, the facts of its caption checked |
| `tools/chain_register.py`, `tools/chapters.py` | The register of every instruction of the finished game: its bank, address, file, line, step, chapter, and whether a test ran it (`reference/register` is the book's) |
| `tools/stella_palette.py` | The colours of the TIA as Stella draws them, into `game/assets/palette_stella.json` |
| `tools/record_audio.py` | Records what Stella plays, for the test of the sound (`tests/verify_0_9.py --audio`) |

`tests/` holds the test bench of chapter 16: `vcs_sim.py`, the
simulator of the 2600; `model.py` and `sound_model.py`, the game and its
sound written again in Python from the design; `stella_run.py`, which
drives Stella from its debugger; `verify_0_9.py`, the tests of the
complete game; `verify_chain.py`, the tests of the steps; `tia_audio.py`
and `audio_check.py`, the test of the sound; `coverage_notes.py`, why
some instructions never run; `check_plan.py` and `check_dungeon.py`, the
plan of the crypt and its sixteen rooms.
