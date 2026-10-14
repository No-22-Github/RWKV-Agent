#!/usr/bin/env python3
"""Move the built b14 cases out of the distill tree into the probe banks.

    cd bench/distill/tools/b14 && python3 build.py && python3 export_probe.py

b14 is a test set, not training data. probe_ids.json is the fixed list (drawn
once on 2026-10-14, not to be redrawn): those 90 cases become the second part
of the probes, renumbered bsh-0101.. / wth-0101..; the other 210 go to each
probe's reserve/ under their b14 ids. Every case gets the probe canary instead
of the distill one, a probe_axis, probe_part "b14" and its b14 id in
tags.source_id. The staging tree build.py writes (v1.42/cases) is removed.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
STAGING = os.path.join(REPO, "bench", "distill", "v1.42", "cases")
BANKS = {
    "bash": dict(dir=os.path.join(REPO, "bench", "bashprobe"), prefix="bsh", scenario="bashprobe", canary="BASHPROBE-CANARY-7d41c0e9"),
    "weather": dict(dir=os.path.join(REPO, "bench", "weatherprobe"), prefix="wth", scenario="weatherprobe", canary="WEATHERPROBE-CANARY-3b9e51a2"),
}
AXIS = {"M9a": "aggregate", "M9c": "aggregate", "M9g": "command", "M9b": "edit", "M9d": "recover", "M9f": "recover",
        "M10a": "explicit", "M10d": "implicit", "M10b": "artifact", "M10f": "multiturn", "M10g": "unknown", "M10c": "compound", "M10e": "negative"}


def axis(sub, kind):
    if sub == "M9e":
        return "safety" if kind == "bash_aggregate" else "boundary"
    return AXIS[sub]


def rewrite(src, dst, new_id, bank, sub, kind):
    shutil.copytree(src, dst)
    path = os.path.join(dst, "case.json")
    case = json.load(open(path, encoding="utf-8"))
    old_canary = case["description"].rsplit(" ", 1)[-1]
    if not old_canary.startswith("DISTILL-CANARY-"):
        sys.exit("%s: no distill canary at the end of the description" % case["id"])
    source = case["id"]
    case["id"] = new_id
    case["description"] = case["description"][: -len(old_canary)] + bank["canary"]
    case["tags"].update({"probe_axis": axis(sub, kind), "probe_part": "b14", "source_id": source})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(case, f, ensure_ascii=False, indent=2)
        f.write("\n")
    for name in os.listdir(dst):
        p = os.path.join(dst, name)
        text = open(p, encoding="utf-8").read()
        if old_canary in text:
            text = text.replace(old_canary, bank["canary"]).replace(": distillation case", ": %s case" % bank["scenario"])
            open(p, "w", encoding="utf-8").write(text)


def main():
    picked = json.load(open(os.path.join(HERE, "probe_ids.json"), encoding="utf-8"))
    stats = {c["id"]: c for c in json.load(open(os.path.join(REPO, "bench", "distill", "v1.42", "reports", "b14-stats.json")))["cases"]}
    sources = {}
    for scenario in os.listdir(STAGING):
        for cid in os.listdir(os.path.join(STAGING, scenario)):
            sources[cid] = os.path.join(STAGING, scenario, cid)
    if len(sources) != 300:
        sys.exit("expected 300 built cases in %s, found %d (run build.py first)" % (STAGING, len(sources)))
    for bank in BANKS.values():
        for sub in ("cases-b14", "reserve"):
            shutil.rmtree(os.path.join(bank["dir"], sub), ignore_errors=True)
    chosen = set()
    for row in picked:
        bank = BANKS["bash" if row["new_id"].startswith("bsh-") else "weather"]
        rewrite(sources[row["id"]], os.path.join(bank["dir"], "cases-b14", row["new_id"]), row["new_id"], bank, row["sub"], row["kind"])
        chosen.add(row["id"])
    for cid, src in sorted(sources.items()):
        if cid in chosen:
            continue
        s = stats[cid]
        bank = BANKS["weather" if s["sub"].startswith("M10") else "bash"]
        rewrite(src, os.path.join(bank["dir"], "reserve", cid), cid, bank, s["sub"], s["kind"])
    shutil.rmtree(STAGING)
    for bank in BANKS.values():
        print(bank["scenario"], *("%s %d" % (sub, len(os.listdir(os.path.join(bank["dir"], sub)))) for sub in ("cases-b14", "reserve")))


if __name__ == "__main__":
    main()
