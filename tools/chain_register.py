"""chain_register.py - the register of coverage of the book
every instruction of the complete game with the step
of the chain that brings it, its chapter, and whether it ran.

    python3 tools/chain_register.py [--sets FOLDER] [--out FOLDER]

The instructions are those of the listings of the last step
(chain/09-the-hunt/game/build, the 1.0 byte for byte), NTSC and
PAL. For each one:

- where it is: bank, address, file and line in the step, line in
  the master (tools/make_chain.py numbered_lines: the master's
  tags give the step);
- the step that brings it (the first step it is in) and the
  chapter that explains it (tools/chapters.py: plan B, the plan
  of the book, by step, file and routine);
- whether it ran, measured twice: by the
  simulator in every test of the complete game
  (tests/verify_0_9.py, from the eight banks) and, on the route
  that Stella plays as well, by the simulator and by Stella's
  access counters (the byte of the opcode read). On the route
  the two must agree, instruction by instruction; an
  instruction that never ran in any test must have its reason
  (tests/coverage_notes.py).

FOLDER of --sets is where tests/verify_0_9.py --out wrote
coverage_sets_ntsc.json and coverage_sets_pal.json (default
evidence/chain/workspace/master_1.0). Without them the register
has only the steps and the chapters.

It also lists the seams (the instructions of earlier steps that
are not in the complete game, by step) and, for each step, how
many instructions it has and how many it brings: the measure of
the chapters for the plan of the book.

Writes register_<tv>.csv, seams.csv and register.json in --out
(default evidence/chain/workspace/register).
"""
import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import make_chain                                   # noqa: E402
import coverage_notes                               # noqa: E402
from chapters import CHAPTERS, chapter              # noqa: E402
from py65.devices.mpu6502 import MPU                # noqa: E402

OPS = {m[0].lower() for m in MPU.disassemble}
LST = re.compile(r"\s*(\d+)\s+([0-9a-fA-F]{4})\s+"
                 r"((?:[0-9a-fA-F]{2}\s)+)\s*(.*)$")
LABEL = re.compile(r"([A-Za-z_][A-Za-z0-9_]*):?(\s|$)")

def same(src, toks):
    """The line of the source is the one of the listing (where a
    macro's {1} stands for its argument)."""
    words = [w.rstrip(":") for w in src.split(";")[0].split()]
    return len(words) == len(toks) and all(
        re.fullmatch(re.sub(r"\\\{\d+\\\}", ".+", re.escape(w)), t)
        for w, t in zip(words, toks))


def macros(lines):
    """name -> (line of MAC, lines in its body) in one file."""
    out, cur = {}, None
    for i, ln in enumerate(lines, 1):
        w = ln.split(";")[0].split()
        if len(w) >= 2 and w[0].upper() == "MAC":
            cur = (w[1], i)
        elif w and w[0].upper() == "ENDM" and cur:
            out[cur[0]] = (cur[1], i - cur[1] - 1)
            cur = None
    return out


def step_sources(step):
    """file -> its numbered lines in the step (make_chain), for
    the 6502 files of the master that the step includes (as
    make_chain.generate finds them, from scalecrown.asm)."""
    out, todo = {}, ["scalecrown.asm"]
    src = os.path.join(ROOT, "game", "src")
    while todo:
        name = todo.pop(0)
        path = os.path.join(src, name)
        if name in out or not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        out[name] = make_chain.numbered_lines(text, step, name, ";")
        todo += make_chain.included([t[4] for t in out[name]])
    return out


FIRST_FILE = {}         # file -> the first step that includes it


def first_steps():
    for step in sorted(make_chain.STEPS, reverse=True):
        for name in step_sources(step):
            FIRST_FILE[name] = step


def instructions(step, tv):
    """Every instruction of the step's listing: bank, address
    ($1000 + the offset in the bank, as the simulator keeps
    them), file, line in the step's file, its master line (with
    the first and last step and whether it is a seam), the text
    and the routine (the last label before it in its file)."""
    folder = os.path.join(ROOT, "chain", make_chain.STEPS[step])
    lst = os.path.join(folder, "game", "build", f"scalecrown_{tv}.lst")
    srcs = step_sources(step)
    texts = {f: [t[4] for t in nl] for f, nl in srcs.items()}
    macs = {f: macros(t) for f, t in texts.items()}
    out, cur, inmac, label, lastnum = [], None, None, {}, {}
    for line in open(lst, errors="replace"):
        if "------- FILE" in line:
            cur = line.split("FILE")[1].split()[0]
            inmac = None
            continue
        m = re.match(r"\s*(\d+)\s+([0-9a-fA-F]{4}|\s{4})", line)
        if not m:
            continue
        num = int(m.group(1))
        # a macro called (listed with the number 0; it is the
        # line after the last one listed): its body follows,
        # numbered from 1
        if num == 0:
            words = line.split(";")[0].split()[2:]
            call = lastnum.get(cur, 0) + 1
            lastnum[cur] = call
            src = texts[cur][call - 1] if cur in texts else ""
            lab = LABEL.match(src)
            if lab and not src[:1].isspace():
                label[cur] = lab.group(1)
            name = next((w for w in words if any(
                w in mm for mm in macs.values())), None)
            inmac = None
            for f, mm in macs.items():
                if name in mm:
                    # (file, line of MAC, body, next, the call)
                    inmac = [f, mm[name][0], mm[name][1], 1,
                             (cur, call)]
            continue
        if inmac and num != inmac[3]:
            inmac = None
        if inmac:
            inmac[3] += 1
            where = (inmac[0], inmac[1] + num)
        else:
            where = (cur, num)
            lastnum[cur] = num
        if not inmac and where[0] in texts and \
                1 <= num <= len(texts[where[0]]):
            src = texts[where[0]][num - 1]
            lab = LABEL.match(src)
            if lab and not src[:1].isspace() and \
                    lab.group(1).upper() not in ("MAC", "ENDM"):
                label[where[0]] = lab.group(1)
        text = LST.match(line)
        if not text:
            continue
        toks = text.group(4).split(";")[0].split()
        op = next((k for k, t in enumerate(toks[:2])
                   if t.lower().split(".")[0] in OPS), None)
        if op is None:
            continue
        a = int(text.group(2), 16)
        f, n = where
        nl = srcs.get(f)
        if not nl or not 1 <= n <= len(nl):
            raise SystemExit(f"step {step} {tv}: {f}:{n} not in the "
                             f"sources")
        master, low, high, seam, src = nl[n - 1]
        low = max(low, FIRST_FILE[f])
        if inmac:
            # an instruction of a macro is in the steps of its
            # call too, and is a seam if the call is
            cf, cn = inmac[4]
            c = srcs[cf][cn - 1]
            low, high = max(low, c[1], FIRST_FILE[cf]), min(high, c[2])
            seam = seam or c[3]
        if not same(src, toks):
            raise SystemExit(f"step {step} {tv}: {f}:{n} is {src!r}, "
                             f"the listing has {toks}")
        out.append(dict(bank=a >> 12, addr=0x1000 | a & 0xFFF,
                        file=f, line=n, master=master, first=low,
                        last=high, seam=seam,
                        text=" ".join(toks[op:]),
                        routine=label.get(inmac[4][0] if inmac
                                          else f, ""),
                        macro=bool(inmac)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default=os.path.join(
        ROOT, "evidence", "chain", "workspace", "master_1.0"))
    ap.add_argument("--out", default=os.path.join(
        ROOT, "evidence", "chain", "workspace", "register"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    last = make_chain.LAST
    first_steps()
    rep = dict(chapters={str(k): v for k, v in CHAPTERS.items()},
               steps={}, tvs={})
    ok = True
    # the steps: how many instructions, how many new, the seams
    seams = {}
    for step in sorted(make_chain.STEPS):
        per = {}
        for tv in ("ntsc", "pal"):
            ins = instructions(step, tv)
            # instructions (as assembled: a macro or the tail of
            # the banks counts at every place) and lines of the
            # source with an instruction (what the book prints)
            lines = {(i["file"], i["master"]) for i in ins}
            per[tv] = dict(
                instructions=len(ins),
                new=sum(1 for i in ins if i["first"] == step
                        and not i["seam"]),
                seam=sum(1 for i in ins if i["seam"]),
                lines=len(lines),
                new_lines=len({(i["file"], i["master"]) for i in ins
                               if i["first"] == step and
                               not i["seam"]}),
                seam_lines=len({(i["file"], i["master"]) for i in ins
                                if i["seam"]}))
            for i in ins:
                if i["seam"]:
                    k = (i["file"], i["master"])
                    s = seams.setdefault(k, dict(
                        file=i["file"], master=i["master"],
                        routine=i["routine"],
                        text=i["text"], steps=f"{i['first']}-"
                        f"{i['last']}", tvs=set()))
                    s["tvs"].add(tv)
        rep["steps"][str(step)] = per
    with open(os.path.join(a.out, "seams.csv"), "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["file", "master line", "routine", "steps",
                    "chapter", "instruction", "tv"])
        for (fn, n), s in sorted(seams.items()):
            w.writerow([fn, n, s["routine"], s["steps"],
                        chapter(int(s["steps"].split("-")[0]), fn,
                                s["routine"]),
                        s["text"], "+".join(sorted(s["tvs"]))])
    rep["seams"] = len(seams)
    # the complete game
    for tv in ("ntsc", "pal"):
        ins = instructions(last, tv)
        path = os.path.join(a.sets, f"coverage_sets_{tv}.json")
        sets = None
        if os.path.exists(path):
            j = json.load(open(path))
            sets = dict(executed={tuple(x) for x in j["executed"]},
                        route={tuple(x) for x in j["route"]},
                        stella={tuple(x) for x in j["stella"]})
        sym = {}
        r = dict(instructions=len(ins), by_step=Counter(),
                 by_chapter=Counter(), by_file=Counter())
        rows, never, disagree, unexplained = [], Counter(), [], []
        for n, i in enumerate(ins, 1):
            ch = chapter(i["first"], i["file"], i["routine"])
            r["by_step"][i["first"]] += 1
            r["by_chapter"][ch] += 1
            r["by_file"][i["file"]] += 1
            ran = route = st = reason = ""
            if sets:
                key = (i["bank"], i["addr"])
                ran = key in sets["executed"]
                route = key in sets["route"]
                st = (i["bank"], i["addr"] & 0xFFF) in sets["stella"]
                if route != st:
                    disagree.append(f"{i['file']}:{i['line']} "
                                    f"{i['text']}")
                if not ran:
                    reason = coverage_notes.reason(i, sym, tv) or ""
                    never[reason or "?"] += 1
                    if not reason:
                        unexplained.append(f"{i['file']}:{i['line']} "
                                           f"{i['text']}")
            rows.append([n, i["bank"], f"${i['addr']:04X}", i["file"],
                         i["line"], i["master"], i["first"], ch,
                         i["routine"], i["text"],
                         {True: "yes", False: "no"}.get(ran, ""),
                         {True: "yes", False: "no"}.get(route, ""),
                         {True: "yes", False: "no"}.get(st, ""),
                         reason])
        with open(os.path.join(a.out, f"register_{tv}.csv"), "w",
                  newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["n", "bank", "address", "file", "line",
                        "master line", "step", "chapter", "routine",
                        "instruction", "ran (all the tests)",
                        "ran (route, simulator)",
                        "read (route, Stella)", "why never"])
            w.writerows(rows)
        r = {k: (dict(sorted((str(a_), b) for a_, b in v.items()))
                 if isinstance(v, Counter) else v) for k, v in r.items()}
        if sets:
            r.update(ran=sum(1 for x in rows if x[10] == "yes"),
                     route_simulator=sum(1 for x in rows
                                         if x[11] == "yes"),
                     route_stella=sum(1 for x in rows
                                      if x[12] == "yes"),
                     never=dict(never), disagree=disagree[:20],
                     disagree_count=len(disagree),
                     unexplained=unexplained[:20],
                     unexplained_count=len(unexplained))
            r["pass"] = not disagree and not unexplained and \
                set(never) == coverage_notes.reasons(tv)
        else:
            r["pass"] = None
        ok &= r["pass"] is not False
        rep["tvs"][tv] = r
    rep["pass"] = ok
    with open(os.path.join(a.out, "register.json"), "w") as f:
        json.dump(rep, f, indent=1)
    for step, per in rep["steps"].items():
        print(f"step {step}: " + ", ".join(
            f"{tv} {v['instructions']} instructions ({v['lines']} "
            f"lines), {v['new']} new ({v['new_lines']}), "
            f"{v['seam']} of seams ({v['seam_lines']})"
            for tv, v in per.items()))
    print(f"seams: {rep['seams']} lines of earlier steps")
    for tv, r in rep["tvs"].items():
        print(f"{tv}: {r['instructions']} instructions; by chapter "
              f"{r['by_chapter']}")
        if r["pass"] is not None:
            print(f"{tv}: ran {r['ran']}, on the route simulator "
                  f"{r['route_simulator']} Stella {r['route_stella']}"
                  f" (disagree {r['disagree_count']}), never "
                  f"{r['never']}, unexplained "
                  f"{r['unexplained_count']}")
    if any(r["pass"] is None for r in rep["tvs"].values()):
        print(f"no coverage sets in {a.sets}: what ran is not in the "
              "register (run tests/verify_0_9.py --out there first)")
    print("REGISTER PASS" if ok else "REGISTER FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
