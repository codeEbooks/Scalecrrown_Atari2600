"""chapters.py - the chapters of the book: which chapter
explains each line of the game.

The plan of the book, plan B: 17 chapters on the chain of nine steps with step 06 in two chapters (the
throne room and its kernel; the Serpent King's rules).

chapter(step, file, routine) gives the chapter of a line of the game
from the step that brings it, its file and the routine it is in (the
register of coverage, tools/chain_register.py, has all three);
CHAPTERS the working titles; CHAPTER_STEP the step each code chapter
builds. Plans A and C, the other plans considered, are kept for
the record.
"""

# A row of the register: step, file, routine. The routines of step 5
# that are the sword and the damage (the rest is the serpents); of
# step 6 those of the throne room's kernel and its pointers (the rest
# is the King's rules); of step 8 those of the title (the rest is the
# states and the end screens).
DAMAGE = {"ga_blade", "ga_bite", "wound", "wo_en", "th_hurt",
          "th_feet", "th_plb", "th_hit", "fr_over", "new_game",
          "prep_room"}
THRONE_KERNEL = {"throne_kernel.asm"}
THRONE_DRAW = {"p1_throne", "pt_king", "pt_dir", "pt_flash",
               "pt_frame", "pt_ptrs", "pr_vcol", "pr_digits",
               "hu_throne", "su_copied", "rs_map", "p1_bands"}
TITLE = {"title_kernel.asm"}
TITLE_MAIN = {"frame_ready", "fr_mode", "fr_start", "fr_new",
              "fr_title", "vb_wait", "kernel_done", "theme"}


def chapter_a(step, file, routine):
    """Plan A: the first plan, on the chain of
    nine steps, 16 chapters (the provisional chapters of the
    register)."""
    if step == 1:
        return {"scalecrown.asm": 2, "main.asm": 3}.get(file, 4)
    if step == 5:
        return 9 if routine in DAMAGE else 8
    if step == 7:
        return 11 if file == "sound.asm" else 12
    return {2: 5, 3: 6, 4: 7, 6: 10, 8: 13, 9: 14}[step]


def chapter_b(step, file, routine):
    """Plan B: as A, and step 6 in two chapters (the throne room's
    kernel; the Serpent King's rules), 17 chapters."""
    a = chapter_a(step, file, routine)
    if a < 10:
        return a
    if a == 10:
        return 10 if file in THRONE_KERNEL or routine in THRONE_DRAW \
            else 11
    return a + 1


def chapter_c(step, file, routine):
    """Plan C: as B, and step 8 in two chapters (the title; the
    states and the end screens), 18 chapters."""
    b = chapter_b(step, file, routine)
    if b < 14:
        return b
    if b == 14:
        return 14 if file in TITLE or routine in TITLE_MAIN else 15
    return b + 1


TITLES_A = {
    1: "Your workshop", 2: "The 6507, the memory and the cartridge",
    3: "Racing the beam: the frame",
    4: "The playfield and the first room", 5: "The knight",
    6: "The dungeon and the HUD", 7: "Keys, doors and treasure",
    8: "The serpents", 9: "The sword and the damage",
    10: "The Serpent King", 11: "The TIA and the music",
    12: "Effects and sound modes", 13: "States, title and end screens",
    14: "The hunt: how hard the game is",
    15: "Reading and checking the game", 16: "Glossary and index"}


def shift(titles, at, new, n=1):
    """Titles with chapter `at` replaced by the chapters `new`."""
    out = {}
    for c, t in titles.items():
        if c < at:
            out[c] = t
        elif c == at:
            for k, t2 in enumerate(new):
                out[c + k] = t2
        else:
            out[c + len(new) - 1] = t
    return out


TITLES_B = shift(TITLES_A, 10, ["The throne room",
                                "The Serpent King"])
TITLES_C = shift(TITLES_B, 14, ["The title",
                                "States and end screens"])

CHAPTERS = TITLES_B
CHAPTER_STEP = {2: 1, 3: 1, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 5, 10: 6,
                11: 6, 12: 7, 13: 7, 14: 8, 15: 9}
chapter = chapter_b


def b_to_a(n):
    """A chapter of plan B in plan A (the two chapters of step 06 are
    A's chapter 10)."""
    return n if n < 10 else (10 if n in (10, 11) else n - 1)
