"""make_variants.py - the variants and the breaks of the chain of
the book, each one made and proved.

    python3 tools/make_variants.py --stella PATH [--ids 1a,2x]
                                   [--out FOLDER]

For each change of tools/variants.py: the step's folder copied,
the lines changed, the step built with its own tools/build.py;
then the step and the changed step play the same inputs (the head
of the step's route, tests/verify_chain.py, NTSC, from bank 0) in
the simulator, and in Stella for the pictures; what the change
claims is checked (tools/variants.py). The report and two
pictures of each (the step, the change: the picture named by
`until`, or the first that differs) go to
evidence/chain/workspace/d3/.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import verify_chain as vc                           # noqa: E402
import verify_0_9 as v9                             # noqa: E402
import stella_run                                   # noqa: E402
import variants                                     # noqa: E402
import model                                        # noqa: E402

TV = "ntsc"
# the variables of the sound player (the model of the game keeps
# only the mode, the song and the requests)
SOUND = {"smode", "sfxi", "mclock", "mstep", "vpos", "vleft", "venv",
         "vins", "vnote"}


def game_names(step):
    """The variables of the game in this step: those of the
    model's state and of the sound player, never the scratch of
    the kernels or the pointers to the tables (a change that
    moves the tables changes them, not the game)."""
    g = model.Game(TV, step)
    if not g.screen:
        g.new_game()
    names = {k.partition("+")[0] for k in g.state() if
             not k.startswith("SC")}
    sc = {k for k in g.state() if k.startswith("SC")}
    if step >= 6:
        sc |= {f"SC+{i}" for i in model.king_bytes()}
    return names | (SOUND if step >= 7 else set()), sc


def ram_names(folder):
    """RAM address -> name (name+k inside a variable of k bytes),
    from the step's scalecrown.asm and its symbols."""
    src = open(os.path.join(folder, "game", "src",
                            "scalecrown.asm")).read().split("\n")
    sym = v9.read_symbols(os.path.join(folder, "game", "build",
                                       f"scalecrown_{TV}.sym"))
    out, ram = {}, False
    for line in src:
        if "SEG.U" in line:
            ram = True
        if "MAC BANK" in line:
            ram = False
        m = re.match(r"([A-Za-z_]\w*)\s+ds\s+(\d+)", line)
        if ram and m and m.group(1) in sym:
            a = sym[m.group(1)]
            for k in range(int(m.group(2))):
                out[a + k] = m.group(1) + (f"+{k}" if k else "")
    return out


def head(d, until):
    """The frames of the route up to the picture named by until
    (a part of its label, or a room: the first picture there),
    and 30 more; the pictures in them."""
    for k in sorted(d.shots):
        st = d.states[k - 1]
        if isinstance(until, int):
            if st.screen and st.room == until:
                break
        elif until in d.shots[k]:
            break
    else:
        raise RuntimeError(f"no picture {until!r} in the route")
    n = min(len(d.inputs), k + 30)
    return n, k, [s for s in sorted(d.shots) if s <= n]


def build_variant(v, work):
    step = v["step"]
    src = os.path.join(vc.CHAIN, vc.STEPS[step])
    dst = os.path.join(work, f"{v['id']}-{vc.STEPS[step]}")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        "build", "generated", "__pycache__"))
    for name, old, new in v["change"]:
        p = os.path.join(dst, name)
        lines = open(p).read().split("\n")
        hits = [i for i, ln in enumerate(lines) if ln.rstrip() == old]
        if len(hits) != 1:
            raise RuntimeError(f"{v['id']}: {name}: {old!r} "
                               f"{len(hits)} times")
        if new:
            lines[hits[0]] = new
        else:
            del lines[hits[0]]
        open(p, "w").write("\n".join(lines))
    r = subprocess.run([sys.executable, "tools/build.py"], cwd=dst,
                       capture_output=True, text=True)
    return dst, r


def first_ram_difference(a, b, names, keep):
    """The first frame and variable of the game (keep: names, SC
    bytes) where the two runs differ."""
    gn, sc = keep
    for k in range(1, min(len(a["ram"]), len(b["ram"]))):
        for i in range(128):
            n = names.get(0x80 + i)
            if n and n.partition("+")[0] in gn and \
                    a["ram"][k][i] != b["ram"][k][i]:
                return k, n
        for i in range(128):
            if f"SC+{i}" in sc and a["sc"][k][i] != b["sc"][k][i]:
                return k, f"SC+{i}"
    return None


def pixels(path):
    from PIL import Image
    return Image.open(path).convert("RGB").tobytes()


def prove(v, stella, out, work, routes):
    t0 = time.time()
    step = v["step"]
    if step not in routes:
        vc.use(step)
        routes[step] = vc.ROUTES[step](TV)
    d = routes[step]
    n, k_until, shots = head(d, v["until"])
    inputs = d.inputs[:n]
    rep = dict(id=v["id"], step=step, kind=v["kind"],
               title=v["title"], text=v["text"],
               change=[dict(file=f, line=old.strip(),
                            becomes=new.strip() or "(taken out)")
                       for f, old, new in v["change"]],
               frames=n, until=d.shots[k_until], claims=v["claims"])
    folder, built = build_variant(v, work)
    rep["builds"] = built.returncode == 0
    if not rep["builds"]:
        rep["why"] = (built.stdout + built.stderr)[-500:]
        rep["pass"] = False
        return rep
    vc.use(step)
    base = v9.simulate(TV, 0, 11, inputs)
    v9.BUILD = os.path.join(folder, "game", "build")
    var = v9.simulate(TV, 0, 11, inputs)
    t = v9.TV[TV]
    timing = var["lines"] == [t["lines"]] and var["vsync"] == [228] \
        and not var["window_error_count"]
    names = ram_names(folder)
    diff = first_ram_difference(base, var, names, game_names(step))
    audio = any(a != b for a, b in zip(base["audio"], var["audio"]))
    rep["facts"] = dict(
        lines=var["lines"], vsync=var["vsync"],
        window_errors=var["window_error_count"],
        first_window_error=var["window_errors"][:1],
        seam_wrong=var["seam"]["wrong"],
        first_ram_difference=dict(frame=diff[0], var=diff[1])
        if diff else None,
        audio_differs=audio,
        step_lines=base["lines"])
    checks = []
    c = v["claims"]
    if "timing" in c:
        checks.append(("timing", timing == c["timing"]))
    if "seam" in c:
        checks.append(("seam", (var["seam"]["wrong"] == 0) == c["seam"]))
    if c.get("ram") == "same":
        checks.append(("ram the same", diff is None))
    elif "ram" in c:
        checks.append(("ram first in " + ", ".join(c["ram"]),
                       bool(diff) and diff[1] in c["ram"]))
    if "audio" in c:
        checks.append(("audio", audio == c["audio"]))
    if "picture" in c and stella:
        rom0 = os.path.join(vc.CHAIN, vc.STEPS[step], "game", "build",
                            f"scalecrown_{TV}.bin")
        rom1 = os.path.join(folder, "game", "build",
                            f"scalecrown_{TV}.bin")
        runs = [stella_run.run(stella, rom, n,
                               joystick=lambda k: inputs[k - 1],
                               shots=shots, startbank=0)
                for rom in (rom0, rom1)]
        differ = [k for k in shots if k in runs[0]["shots"] and
                  k in runs[1]["shots"] and
                  pixels(runs[0]["shots"][k]) !=
                  pixels(runs[1]["shots"][k])]
        rep["facts"]["pictures_differ"] = len(differ)
        rep["facts"]["pictures"] = len(shots)
        pick = k_until if k_until in differ else (
            differ[0] if differ else k_until)
        for tag, r in zip(("step", "change"), runs):
            if pick in r["shots"]:
                shutil.copy(r["shots"][pick], os.path.join(
                    out, f"{v['id']}_{tag}.png"))
            shutil.rmtree(r["work"], ignore_errors=True)
        rep["picture_frame"] = pick
        checks.append(("picture", bool(differ) == c["picture"]))
    rep["checks"] = [dict(check=a, passed=bool(b)) for a, b in checks]
    rep["pass"] = all(b for _, b in checks)
    rep["seconds"] = round(time.time() - t0)
    vc.use(step)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stella")
    ap.add_argument("--ids")
    ap.add_argument("--out", default=os.path.join(
        ROOT, "evidence", "chain", "workspace", "d3"))
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ids = set(a.ids.split(",")) if a.ids else None
    work = tempfile.mkdtemp(prefix="chain_var_")
    routes, allok = {}, True
    try:
        for v in variants.VARIANTS:
            if ids and v["id"] not in ids:
                continue
            path = os.path.join(a.out, f"{v['id']}.json")
            if os.path.exists(path) and not a.redo:
                rep = json.load(open(path))
                print(f"{v['id']}: done before, "
                      f"{'PASS' if rep['pass'] else 'FAIL'}")
                allok &= rep["pass"]
                continue
            rep = prove(v, a.stella, a.out, work, routes)
            json.dump(rep, open(path, "w"), indent=1)
            allok &= rep["pass"]
            f = rep.get("facts", {})
            print(f"{v['id']} {v['kind']} {v['title']}: "
                  f"{'PASS' if rep['pass'] else 'FAIL'} "
                  f"{[c['check'] for c in rep.get('checks', []) if not c['passed']]} "
                  f"lines {f.get('lines')} windows "
                  f"{f.get('window_errors')} ram "
                  f"{f.get('first_ram_difference')} audio "
                  f"{f.get('audio_differs')} pictures "
                  f"{f.get('pictures_differ')}/{f.get('pictures')} "
                  f"{rep.get('seconds')} s", flush=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("VARIANTS PASS" if allok else "VARIANTS FAIL")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
