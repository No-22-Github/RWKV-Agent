#!/usr/bin/env python3
"""calibrate.py — flag cases whose measured pass rate contradicts their declared level.

Aggregates ledger/cases.jsonl across ALL runs (every config, every k) per case
and compares against tags.level (recorded at ingest time from the case tags):

  L1/L2 with pass rate < 20% in every config  -> harder_than_declined
  L3   with pass rate > 80% in every config   -> easier_than_declined
  L0   with overall pass rate < 50%           -> l0_too_hard

Output: a markdown table on stdout. Stdlib only.
"""
import argparse
import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
CASES_JSONL = TOOLS_DIR.parent / "ledger" / "cases.jsonl"


def read_jsonl(path):
    path = Path(path)
    if not path.is_file():
        return []
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            print("warning: %s:%d is not valid JSON, skipped" % (path, i), file=sys.stderr)
    return rows


def collect():
    per_case = {}
    for row in read_jsonl(CASES_JSONL):
        cid = row.get("case_id")
        if cid is None:
            continue
        d = per_case.setdefault(cid, {"level": None, "configs": {}, "total": [0, 0]})
        if d["level"] is None and row.get("level"):
            d["level"] = row["level"]
        cfg = row.get("config_name") or "unknown"
        g = d["configs"].setdefault(cfg, [0, 0])
        g[1] += 1
        d["total"][1] += 1
        if row.get("passed"):
            g[0] += 1
            d["total"][0] += 1
    return per_case


def classify(level, config_rates, overall_rate):
    """Return the deviation flag for one case, or '-'."""
    if level in ("L1", "L2"):
        if config_rates and all(r < 0.20 for r in config_rates):
            return "harder_than_declined"
    elif level == "L3":
        if config_rates and all(r > 0.80 for r in config_rates):
            return "easier_than_declined"
    elif level == "L0":
        if overall_rate is not None and overall_rate < 0.50:
            return "l0_too_hard"
    return "-"


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Flag cases whose measured pass rate contradicts their declared difficulty level.")
    ap.add_argument("--ledger", default=str(CASES_JSONL),
                    help="path to cases.jsonl (default: bench/workbank/ledger/cases.jsonl)")
    args = ap.parse_args(argv)

    per_case = collect()
    if not per_case:
        print("no cases in ledger (%s)" % args.ledger)
        return 0

    entries = []
    for cid in sorted(per_case):
        d = per_case[cid]
        total_p, total_n = d["total"]
        overall = (total_p / total_n) if total_n else None
        config_rates = [p / n for p, n in d["configs"].values() if n]
        flag = classify(d["level"], config_rates, overall)
        config_cell = ", ".join("%s %.0f%%" % (cfg, 100 * p / n)
                                for cfg, (p, n) in sorted(d["configs"].items()))
        entries.append({
            "case": cid, "level": d["level"] or "unknown", "flag": flag,
            "configs": config_cell,
            "overall": "%.0f%% (%d/%d)" % (100 * overall, total_p, total_n) if total_n else "-",
        })

    flagged = [e for e in entries if e["flag"] != "-"]
    print("# workbank calibration (declared level vs measured pass rate)")
    print()
    print("| case | level | per-config pass | overall | flag |")
    print("|---|---|---|---|---|")
    for e in sorted(entries, key=lambda e: (e["flag"] == "-", e["case"])):
        print("| %s | %s | %s | %s | %s |" % (e["case"], e["level"], e["configs"], e["overall"], e["flag"]))
    print()
    print("flagged %d / %d cases; rules: L1/L2 all-config <20%% => harder_than_declined, "
          "L3 all-config >80%% => easier_than_declined, L0 <50%% => l0_too_hard"
          % (len(flagged), len(entries)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
