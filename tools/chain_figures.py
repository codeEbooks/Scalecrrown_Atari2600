"""chain_figures.py - the figures of the book, from the chain.

    python3 tools/chain_figures.py --stella PATH [--ids 01,02]
                                   [--out FOLDER] [--check]

For each step and television of tools/figure_list.py: the route
of the step (tests/verify_chain.py), up to its last figure,
played twice in Stella 7.0 from bank 0, with a capture at each
figure's frame. A figure passes when:

- the two captures are the same file, byte for byte, and the RAM
  of that frame is the same in the two runs;
- the facts of its caption hold on that RAM (figure_list.py);
- the RAM is the model's (tests/model.py, the step's model) and
  the picture is the one drawn from what the model's frame
  showed (tests/verify_0_9.py expected), pixel by pixel.

--check builds the routes and checks the facts on the model
only (no Stella), to try the list. --relabel writes only the
chapters and captions of figure_list.py into figures.json and
makes the sheet again (when the plan of the chapters changes).

Writes in --out (default evidence/chain/workspace/figures):
FIG_NN_<step>_<tv>.png (Stella's capture, 320 pixels wide: two
per pixel of the TIA), print/FIG_NN_x4.png (four times larger,
without interpolation, for print), figures.json (every figure:
its frame, caption, facts, checks, SHA-256 of the two captures,
the version of Stella) and FIGURE_CATALOGO.png (all the figures
with their numbers, to look at).
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "game", "assets"))
import verify_chain as vc                           # noqa: E402
import verify_0_9 as v9                             # noqa: E402
import stella_run                                   # noqa: E402
import figure_list                                  # noqa: E402
import dungeon                                      # noqa: E402
from make_variants import ram_names                 # noqa: E402


def level(room):
    return dungeon.ROOMS[room]["level"]


def frame_of(d, fig):
    """The frame of the figure: the picture of the route whose
    label is the shot, or the only one that starts with it, or
    the only one that has it; then the offset."""
    labels = sorted(d.shots.items())
    for test in (lambda s: s == fig["shot"],
                 lambda s: s.startswith(fig["shot"]),
                 lambda s: fig["shot"] in s):
        hits = [k for k, s in labels if test(s)]
        if len(hits) == 1:
            return hits[0] + fig.get("offset", 0)
        if len(hits) > 1:
            raise SystemExit(f"figure {fig['id']}: {fig['shot']!r} "
                             f"is {len(hits)} pictures")
    raise SystemExit(f"figure {fig['id']}: no picture "
                     f"{fig['shot']!r} in the route of step "
                     f"{fig['step']}")


def values(state):
    """The variables of a model's state, and points and level."""
    v = {k: x for k, x in state.items() if not k.startswith("SC")}
    if "score" in v:
        v["points"] = int(f"{v['score']:02x}{v['score+1']:02x}"
                          f"{v['score+2']:02x}")
    if v.get("screen"):
        v["level"] = level(v["room"])
    return v


def ram_values(ram, names):
    """The same from a RAM dump ($80-$FF) and the step's names."""
    v = {name: ram[a - 0x80] for a, name in names.items()}
    if "score" in v:
        v["points"] = int(f"{v['score']:02x}{v['score+1']:02x}"
                          f"{v['score+2']:02x}")
    if v.get("screen") and "room" in v:
        v["level"] = level(v["room"])
    return v


def check_facts(fig, now, at):
    """The facts of the caption on the values of the frame (now);
    at(shot) gives the values of the frame of another picture."""
    out = []
    for f in fig["facts"]:
        var = f[0]
        if len(f) == 2:
            want, got = f[1], now.get(var)
            out.append(dict(fact=f"{var} = {want}", value=got,
                            passed=got == want))
        else:
            delta, since = int(f[1]), f[2]
            then, got = at(since).get(var), now.get(var)
            ok = then is not None and got is not None and \
                got - then == delta
            out.append(dict(fact=f"{var} {f[1]} since {since!r}",
                            value=f"{then} -> {got}", passed=ok))
    return out


def groups(ids):
    out = {}
    for fig in figure_list.FIGURES:
        if ids and fig["id"] not in ids:
            continue
        out.setdefault((fig["step"], fig["tv"]), []).append(fig)
    return out


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run_group(step, tv, figs, stella, palette, out, check_only):
    t0 = time.time()
    vc.use(step)
    d = vc.ROUTES[step](tv)
    frames = {fig["id"]: frame_of(d, fig) for fig in figs}
    reps = []
    if check_only:
        for fig in figs:
            k = frames[fig["id"]]
            now = values(d.states[k - 1].state())
            facts = check_facts(fig, now, lambda s: values(
                d.states[frame_of(d, dict(fig, shot=s, offset=0))
                         - 1].state()))
            reps.append(dict(id=fig["id"], step=step, tv=tv, frame=k,
                             label=d.shots.get(k, ""), facts=facts,
                             passed=all(f["passed"] for f in facts)))
        return reps, round(time.time() - t0)
    folder = os.path.join(vc.CHAIN, vc.STEPS[step])
    rom = os.path.join(folder, "game", "build",
                       f"scalecrown_{tv}.bin")
    names = ram_names(folder) if tv == "ntsc" else None
    if names is None:                   # (the same names in PAL)
        names = ram_names(folder)
    n = max(frames.values()) + 1
    shots = sorted(set(frames.values()))
    runs = [stella_run.run(stella, rom, n,
                           joystick=lambda k: d.inputs[k - 1],
                           shots=shots, startbank=0)
            for _ in range(2)]
    sym = v9.read_symbols(os.path.join(folder, "game", "build",
                                       f"scalecrown_{tv}.sym"))
    for fig in figs:
        k = frames[fig["id"]]
        name = f"FIG_{fig['id']}_step{step:02d}_{tv}"
        why = []
        caps = [r["shots"].get(k) for r in runs]
        rams = [r["ram"][k - 1] for r in runs]
        if None in caps:
            why.append("no capture")
        if None in rams:
            why.append("no RAM")
        shas = [sha(c) for c in caps if c]
        if len(shas) == 2 and shas[0] != shas[1]:
            why.append("the two captures differ")
        if None not in rams and rams[0] != rams[1]:
            why.append("the RAM of the two runs differs")
        facts, model_diff, wrong = [], None, None
        if not why:
            now = ram_values(rams[0], names)

            def at(s, fig=fig):
                j = frame_of(d, dict(fig, shot=s, offset=0))
                return ram_values(runs[0]["ram"][j - 1], names)
            facts = check_facts(fig, now, at)
            if not all(f["passed"] for f in facts):
                why.append("a fact of the caption does not hold")
            g = d.states[k - 1]
            model_diff = [
                dict(var=v, model=want,
                     ram=rams[0][sym[v.partition("+")[0]] - 0x80 +
                                 int(v.partition("+")[2] or 0)])
                for v, want in g.state().items()
                if not v.startswith("SC") and
                rams[0][sym[v.partition("+")[0]] - 0x80 +
                        int(v.partition("+")[2] or 0)] != want]
            if model_diff:
                why.append(f"RAM and model differ: {model_diff[:3]}")
            cmp = v9.compare(v9.expected(tv, g), caps[0], tv,
                             palette[tv])
            wrong = cmp["wrong"]
            if wrong:
                why.append(f"{wrong} pixels differ from the model's "
                           f"picture ({cmp['first']})")
            shutil.copy(caps[0], os.path.join(out, name + ".png"))
            from PIL import Image
            im = Image.open(caps[0]).convert("RGB")
            im.resize((im.width * 4, im.height * 4),
                      Image.NEAREST).save(os.path.join(
                          out, "print", f"FIG_{fig['id']}_x4.png"))
        reps.append(dict(
            id=fig["id"], step=step, tv=tv, chapter=fig["chapter"],
            frame=k, label=d.shots.get(k, f"{d.shots.get(k - fig.get('offset', 0), '')} (+{fig.get('offset', 0)})"),
            caption=fig["caption"] + (
                f" (PAL; {runs[0]['version']}.)" if tv == "pal"
                else ""),
            file=name + ".png", sha256=shas, facts=facts,
            pixels_wrong=wrong, model_differences=len(model_diff or []),
            stella=runs[0]["version"], why=why, passed=not why))
    for r in runs:
        shutil.rmtree(r["work"], ignore_errors=True)
    return reps, round(time.time() - t0)


def sheet(reps, out):
    """All the figures, numbered, to look at (not for print)."""
    from PIL import Image, ImageDraw
    ims = [(r, Image.open(os.path.join(out, r["file"])).convert("RGB"))
           for r in reps if r["passed"]]
    if not ims:
        return
    cols, w = 4, 320
    h = max(im.height for _, im in ims) + 30
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new("RGB", (cols * (w + 10) + 10, rows * (h + 10) + 10),
                   (24, 24, 24))
    dr = ImageDraw.Draw(sh)
    for i, (r, im) in enumerate(ims):
        x = 10 + (i % cols) * (w + 10)
        y = 10 + (i // cols) * (h + 10)
        dr.text((x, y + 2), f"FIG {r['id']}  step {r['step']} "
                f"{r['tv'].upper()}  ch. {r['chapter']}",
                fill=(230, 230, 230))
        dr.text((x, y + 14), r["label"][:52], fill=(170, 170, 170))
        sh.paste(im, (x, y + 28))
    sh.save(os.path.join(out, "FIGURE_CATALOGO.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stella")
    ap.add_argument("--ids")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--relabel", action="store_true",
                    help="only the chapters and captions of "
                    "figures.json from figure_list.py, and the sheet "
                    "(the captures are not made again)")
    ap.add_argument("--out", default=os.path.join(
        ROOT, "evidence", "chain", "workspace", "figures"))
    a = ap.parse_args()
    ids = set(a.ids.split(",")) if a.ids else None
    if a.relabel:
        path = os.path.join(a.out, "figures.json")
        rep = json.load(open(path))
        cat = {f["id"]: f for f in figure_list.FIGURES}
        for r in rep["figures"]:
            f = cat[r["id"]]
            r["chapter"] = f["chapter"]
            r["caption"] = f["caption"] + (
                f" (PAL; {r['stella']}.)" if r["tv"] == "pal" else "")
        json.dump(rep, open(path, "w"), indent=1)
        sheet(rep["figures"], a.out)
        print(f"{len(rep['figures'])} figures relabelled")
        return 0
    palette = json.load(open(os.path.join(ROOT, "game", "assets",
                                          "palette_stella.json")))
    if not a.check:
        if not a.stella:
            raise SystemExit("--stella is needed (or --check)")
        os.makedirs(os.path.join(a.out, "print"), exist_ok=True)
    allrep, ok = [], True
    for (step, tv), figs in sorted(groups(ids).items()):
        reps, secs = run_group(step, tv, figs, a.stella, palette,
                               a.out, a.check)
        for r in reps:
            ok &= r["passed"]
            bad = [f["fact"] + f" ({f['value']})"
                   for f in r["facts"] if not f["passed"]]
            print(f"FIG {r['id']} step {step} {tv} frame {r['frame']}"
                  f": {'PASS' if r['passed'] else 'FAIL'} "
                  f"{r.get('why', '')} {bad}", flush=True)
        print(f"step {step} {tv}: {len(reps)} figures, {secs} s",
              flush=True)
        allrep += reps
    if not a.check:
        path = os.path.join(a.out, "figures.json")
        old = json.load(open(path))["figures"] if ids and \
            os.path.exists(path) else []
        keep = {r["id"]: r for r in old}
        keep.update({r["id"]: r for r in allrep})
        allrep = [keep[k] for k in sorted(keep)]
        json.dump(dict(figures=allrep,
                       passed=all(r["passed"] for r in allrep)),
                  open(path, "w"), indent=1)
        sheet(allrep, a.out)
    print("FIGURES PASS" if ok else "FIGURES FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
