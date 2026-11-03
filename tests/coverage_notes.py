"""coverage_notes.py - why some instructions of Scalecrown never
run in the tests (milestones 0.9-0.9.4).

verify_0_9.py runs every test from each of the eight banks in
the simulator and keeps every instruction that ran. The
instructions of the listing that never ran must each have a
reason here, and every reason must still hold (an instruction
it covers never ran). The book writes these as its "Limits".

reason(ins, sym, tv) gives the key of the reason for an
instruction of the listing (a dict: bank, addr - $1000 + the
offset in the bank -, file, text) of the cartridge for tv, or
None. REASONS says it in words; reasons(tv) are the keys that
must hold for tv (0.9.4: one holds in NTSC only).
"""

TAIL = 0xFAA            # where the tail of every bank starts

REASONS = {
    "tail": (
        "The tail of the banks (scalecrown.asm, TAIL, from $FAA): "
        "the same 70 bytes in all eight banks, so that a "
        "trampoline works from any bank. Each trampoline runs its "
        "first instruction (sta F4Bn, the bank switch) in the bank "
        "that calls it and the rest in the bank it switches to: "
        "the copies in the other banks never run. The reset "
        "trampoline ($FE0) runs in all eight, from the eight start "
        "banks."),
    "sprint2": (
        "0.9.4, the second pixel of the sprint (things.asm, "
        "ga_crawl: jsr ga_step, two pixels) in NTSC: a chasing "
        "serpent crawls 50 to 56 pixels a second (rules.py, "
        "SPRINT_PX_S), less than a pixel a frame at 60 frames a "
        "second, so in NTSC the sprint is never two pixels; in "
        "PAL, at 50 frames, it is from level 2 on, and the tests "
        "run it there."),
}


def reasons(tv):
    """The keys of the reasons that must hold for tv."""
    return {"tail", "sprint2"} if tv == "ntsc" else {"tail"}


def reason(ins, sym, tv):
    """The key of the reason why instruction ins never runs, or
    None."""
    if ins["file"] == "scalecrown.asm" and \
            ins["addr"] & 0x0FFF >= TAIL:
        return "tail"
    if tv == "ntsc" and ins["file"] == "things.asm" and \
            ins["text"].split(";")[0].split() == ["jsr", "ga_step"]:
        return "sprint2"
    return None
