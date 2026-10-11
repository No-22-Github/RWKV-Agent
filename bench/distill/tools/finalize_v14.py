#!/usr/bin/env python3
"""Freeze current v1.4 (+b13) without new teacher calls or semantic row edits.

python3 bench/distill/tools/finalize_v14.py --out local/runs/distill/v14/final-20261011
Uses existing pack, suffix and segments tools. Refuses an existing output root.
"""
import argparse
import collections
import hashlib
import json
import subprocess
from pathlib import Path

import v14_composition as composition
from b13.report_stats import count
from build_v13_suffix import SUFFIX, add_suffix
from to_segments import segments
from distill_paths import REPO, EXCLUDE_JSONL


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    root = Path(REPO)
    if Path.cwd().resolve() != root.resolve():
        raise ValueError("run from repository root")
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    extra = root / "local/runs/distill/v141/b13/corpus/rows.jsonl"
    paths = [Path(p) for p in composition.SOURCES] + [extra]
    excludes = collections.defaultdict(set)
    for line in Path(EXCLUDE_JSONL).read_text().splitlines():
        if line.strip():
            e = json.loads(line)
            excludes[e["case_id"]].add(e.get("batch", ""))
    rows, removed, appended, existing = [], 0, 0, 0
    input_counts = {}
    for path in paths:
        raw = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        kept = 0
        for row in raw:
            m = row["meta"]
            banned = excludes.get(m["case_id"], set())
            if banned and ("" in banned or not m.get("source") or composition.batch_of(m) in banned):
                removed += 1
                continue
            assert m["case_tags"].get("family"), m["case_id"]
            assert row["loss_spans"][-1][1] == len(row["text"]), m["case_id"]
            if row["text"].endswith(SUFFIX):
                assert not row["text"].endswith(SUFFIX * 2), m["case_id"]
                existing += 1
            else:
                row = add_suffix(row)
                appended += 1
            segments(row["text"], row["loss_spans"])
            rows.append(row)
            kept += 1
        input_counts[str(path.relative_to(root))] = dict(raw=len(raw), kept=kept, sha256=sha(path))
    baseline = count([extra])
    assert baseline["rows"] == len(rows)
    split = {"train": [], "validation": []}
    cases, families = collections.defaultdict(set), collections.defaultdict(set)
    for row in rows:
        m = row["meta"]
        family = m["case_tags"]["family"]
        side = "validation" if int(hashlib.sha256(family.encode()).hexdigest(), 16) % 32 == 0 else "train"
        split[side].append(row)
        cases[m["case_id"].rsplit("--p", 1)[0]].add(side)
        families[family].add(side)
    assert all(len(v) == 1 for v in cases.values())
    assert all(len(v) == 1 for v in families.values())
    assert len({sha_text(r["text"]) for r in rows}) == len(rows)
    out.mkdir(parents=True)
    for side, selected in split.items():
        source = out / (side + "-rows.jsonl")
        source.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in selected))
        dest = out / "dataset" / side
        run(root, out / (side + "-pack.log"), ["local/bin/rwkv-lab", "corpus", "pack", "--rows", str(source),
            "--exclude", EXCLUDE_JSONL, "--max-tokens", "8128", "--out", str(dest)])
        run(root, out / (side + "-segments.log"), ["python3", "bench/distill/tools/to_segments.py", "--rows", str(dest / "rows.jsonl"), "--out", str(dest / "segments.jsonl")])
        run(root, out / (side + "-segcheck.log"), ["local/bin/rwkv-lab", "corpus", "segcheck", str(dest / "segments.jsonl")])
    summary = dict(status="v1.4_frozen_with_known_data_gaps", composition=baseline,
        input_counts=input_counts, exclude_sha256=sha(EXCLUDE_JSONL),
        split_method="sha256(family) mod 32 == 0 -> validation",
        rows=len(rows), train=len(split["train"]), validation=len(split["validation"]),
        unique_base_cases=len(cases), families=len(families),
        suffix_already_present=existing, suffix_appended=appended, family_leakage=0, case_leakage=0,
        seeded_from_test_rows=sum(bool(r["meta"].get("seeded_from_test")) for r in rows),
        seeded_from_test_by_split={k: sum(bool(r["meta"].get("seeded_from_test")) for r in rs) for k, rs in split.items()},
        wire_hash=sorted({r["meta"]["wire_hash"] for r in rows}),
        pack_manifests={k: json.loads((out / "dataset" / k / "manifest.json").read_text()) for k in split},
        artifact_sha256={str(p.relative_to(out)): sha(p) for p in sorted((out / "dataset").glob("*/*")) if p.is_file()},
        deferred=["first-turn zero-call, list_files, data_query and small-catalog composition gaps",
                  "legacy same-file readback, DONE and M6 whole-file behavior repair",
                  "80 retained test-seeded base700 rows: evaluate only with source-aware clean benchmarks",
                  "think-full/MiSS rendering and student training/evaluation"])
    dump(out / "final-stats.json", summary)
    dump(out / "release-manifest.json", dict(rows=len(rows), split=summary["split_method"],
        inputs=input_counts, exclude_sha256=summary["exclude_sha256"],
        artifacts=summary["artifact_sha256"], stats_sha256=sha(out / "final-stats.json"),
        lab_sha256=sha(root / "local/bin/rwkv-lab"), finalizer_sha256=sha(__file__)))
    print(json.dumps({k: summary[k] for k in ("rows", "train", "validation", "families", "suffix_already_present", "suffix_appended", "seeded_from_test_rows")}, ensure_ascii=False))


def sha_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def run(root, log, cmd):
    result = subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_text(result.stdout)
    print(result.stdout, end="")
    result.check_returncode()


if __name__ == "__main__":
    main()
