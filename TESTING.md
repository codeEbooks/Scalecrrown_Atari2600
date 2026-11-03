# What was tested, and the limits

Everything here ran in emulation: in Stella, the emulator, and in the
book's test bench (`tests/`), a simulator of the 2600 written in Python
for the book. Nothing was run on a real console. Chapter 16 of the
book, "Reading and checking the game", tells how the tests work in its
part "How the book was checked"; this page gives the results, the
versions and what the package cannot repeat.

## The versions

| Program | Versions used |
|---|---|
| dasm | 2.20.14.1 on Linux; `dasm.exe` 2.20.14.1 for Windows, under wine 9.0: the same cartridges, byte for byte |
| Stella | 7.0 on Linux; 7.0c for Windows, under wine 9.0, for steps 01 and 02, their six experiments and the first seven figures: the same results. Stella 6.7 will not do: its debugger does not press SELECT and RESET |
| Python | 3.13; the builds and `verify.py` need 3.10 or later, with its standard library only |
| py65 | 1.2.0 |
| Pillow | 12.3 |
| numpy | 2.5, for the test of the sound |

## The results printed in the book

| Check | Result |
|---|---|
| The route of the finished game | 17 808 frames on NTSC and 15 249 on PAL: the title and its three sound modes, the whole crypt and VICTORY, then GAME OVER twice; 87 pictures named on the way. Played by the simulator from each of the eight banks, with the RAM and the Superchip at random, and by Stella 7.0 |
| Every frame of every test of the finished game | 262 lines on NTSC, 312 on PAL; VSYNC 228 cycles; no store to the TIA out of its window; the game and the sound the model's |
| Stella and the simulator, on the route | The RAM equal in every frame; 87 of 87 pictures equal to the drawing; the bytes of the cartridge read the same (17 501 on NTSC, 17 519 on PAL) |
| The other tests of the finished game | Two random games, the extremes (every column, height and pose, every room closed and open), the songs to their end: no difference from the model |
| Instructions run by the tests | 3 360 of 3 519 on NTSC, 3 390 of 3 548 on PAL; each one never run has its reason (`tests/coverage_notes.py`): 158 copies of the tail of the banks, and on NTSC the second pixel of a sprint |
| Mistakes put into the finished game on purpose | 173 of 173 caught (151 in `game/src`, 22 in the Python that makes the data) |
| The nine steps (`tests/verify_chain.py`) | Each with a route of its own, in the simulator from banks 0 and 7 and in Stella from bank 0, NTSC and PAL: 150 475 frames and 658 pictures in all; 27 of 27 mistakes caught |
| The 27 experiments (`tools/make_variants.py`) | 18 variants keep their time and change what they say; 9 "Where it breaks" versions break what the chapter says |
| The figures (`tools/chain_figures.py`) | 46 figures, each captured twice: the same bytes; the 83 facts of their captions true on the RAM of their frame |
| The sound (`--audio`) | The title recorded from Stella 7.0 against the sound of the model's registers: 26 notes on each television, the worst 5.1 cents off on NTSC and 5.0 on PAL |

## Checked again for this package

The package as it is here was checked on 2 November 2026, on Linux,
from copies of this folder: Python 3.13.16, dasm 2.20.14.1, Stella 7.0,
py65 1.2.0, Pillow 12.3. The tests with Stella (from
`tools/make_variants.py` to `tools/chain_figures.py`) ran on a copy made
earlier the same day: the same cartridges, sources, tests and tools,
with only some comments and texts changed since.

| Check | Result |
|---|---|
| `python verify.py` | Every file unchanged; the complete game, the 9 steps and the 27 experiments built again: 37 of 37 identical, NTSC and PAL; the 27 experiments their steps with the chapters' changes; `releases/` the cartridges of `game` and of step 09 |
| `python verify.py --dasm` with `dasm.exe` 2.20.14.1 for Windows, under wine 9.0 | The same: 37 of 37 identical |
| A copy with every text file in CR LF line ends, as a checkout on Windows may make it | `verify.py`: PASS |
| `Scalecrown_package_1.0.zip`, extracted | The same files; `verify.py`: PASS |
| `tools/make_chain.py --assemble --out` another folder | The nine steps identical to those here, the same fingerprints in `chain.json`, step 09 the release |
| `tools/make_chain.py --assemble` here, then `tools/build.py` at the root | Nothing changes: every file the same |
| `tools/make_variants.py` | 27 of 27 pass, each with what Table 16.9 prints; their reports are those in the experiments' `evidence/` folders, and their 30 pictures are the bytes of the book's run |
| `tests/verify_chain.py --mutations` | Each of the nine steps on its route, NTSC and PAL, in the simulator from banks 0 and 7 and in Stella from bank 0: PASS, with the frames and the pictures of the book, 150 475 and 658; the three mistakes of each step caught, 27 of 27 on NTSC and 27 of 27 on PAL; the reports the same as the book's run, apart from the time taken and the mistakes on PAL, which that run did not try |
| `tools/chain_figures.py` | 46 of 46 figures pass: each captured twice in Stella, the same bytes; the 83 facts of their captions true on the RAM of their frames; every capture the same bytes as the book's run |
| `tests/check_plan.py`, `tests/check_dungeon.py` | PASS |
| `tools/chain_register.py`, with the instructions that the book's run of `tests/verify_0_9.py` ran | The register of `reference/register`, byte for byte |

`tests/verify_0_9.py`, the tests of the complete game, was not run again from this package: it takes hours. Its results are those printed in the book, above; its code is the one that gave them.

## What the package cannot repeat

- **The pages of the book.** Its figures come from captures that
  `tools/chain_figures.py` takes again; the book's own tools, which are
  not here, cropped, enlarged and laid out the captures, and drew the
  diagrams.
- **The reports of the tests.** They are not included, apart from those
  of the experiments, in their folders: running a test writes its report
  again, in `evidence/`.
- **The recordings of the sound.** Not included: `tests/verify_0_9.py
  --audio` records the title again with `tools/record_audio.py`.
- **The probe of chapter 16.** The book prints its program, to be
  typed.

The register of every instruction (`reference/register/`) is the book's.
Its addresses are those the 6507's 13 address lines see, $1000 to
$1FFF in every bank, with the bank in a column of its own; the book
writes bank n from $1000 + $2000 × n (bank 4's $15DB is the book's
$95DB, and $45DB in the listing).
`tools/chain_register.py` makes the register again, in
`evidence/chain/workspace/register`, from the instructions that the
tests of the finished game ran: run `tests/verify_0_9.py --out
evidence/chain/workspace/master_1.0` first (without them the columns of
what ran stay empty).

The tests and their tools are those that checked the book, as they
were. Their comments call the working versions of the game before the
1.0 "milestones", 0.2 to 0.9.4; a few of their reports keep the names
they had then (`MAPPA_DUNGEON_1.0.png`, `FIGURE_CATALOGO.png`: the map
of the crypt and the catalogue of the figures).

## Limits

- A test compares the program with models written in Python for this
  purpose. A model could be wrong in the same way as the program; the
  drawing of the pictures from the design, written apart from the
  generator of the data, and the mistakes above, which the tests had to
  catch, are there to make that unlikely, not impossible.
- A route is one way through the game. It walks to the chests and the
  doors, fights the serpents, takes the stairs and beats the King, but
  it cannot try every timing.
- `verify.py` proves that the cartridges are built byte for byte as in
  the book. After your own changes it will report differences, as it
  should; only playing and testing tell whether a change works.
- Whether a television keeps a steady picture is the set's to say: no
  real console and no real television were part of the tests.
