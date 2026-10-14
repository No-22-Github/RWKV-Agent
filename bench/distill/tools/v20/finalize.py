#!/usr/bin/env python3
"""Pack the v2.0 per-step g1k-think rows into a MiSS training set.

    python3 bench/distill/tools/v20/finalize.py --batch pilot [--batch ...] \
        --out local/runs/distill/v20/final-<date>

Inputs: local/runs/distill/v20/<batch>/corpus/rows.jsonl (render.sh output).
Steps, same discipline as the 1.x finalizers:
  - every row gains the "\\n\\nUser:" turn suffix inside its last loss span
    (the 1.x final-answer-without-EOS lesson; after a tool call the next bytes
    are also "\\n\\nUser:", the tool response turn);
  - sha256(family) % 32 == 0 -> validation, so one trajectory's step rows
    and its family never straddle the split;
  - rows over 8128 tokens are dropped first (late steps after a large read);
  - corpus pack (--max-tokens 8128), to_segments, segcheck per side;
  - the train segments are also written shuffled with a fixed seed
    (segments-shuffled.jsonl): the trainer reads files in order, and the step
    rows of one trajectory would otherwise sit next to each other.
Refuses an existing output root. Writes final-stats.json with the composition.
"""
import argparse
import collections
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build_v13_suffix import SUFFIX, add_suffix  # noqa: E402
from distill_paths import REPO  # noqa: E402

LAB = "local/bin/rwkv-lab-v20"
SEED = 20261014
MAX_TOKENS = 8128
CALL = re.compile(r'<tool_call>\{"name":"(\w+)"')
CJK = re.compile(r"[一-鿿]")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(root, log, cmd):
    result = subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_text(result.stdout)
    print(result.stdout, end="")
    result.check_returncode()


def composition(rows):
    traj = {(r["meta"]["case_id"], r["meta"]["turn"]) for r in rows}
    out = {"rows": len(rows), "trajectories": len(traj), "cases": len({c for c, _ in traj})}
    outputs = [r["text"][r["loss_spans"][-1][0]:r["loss_spans"][-1][1]] for r in rows]
    out["empty_think_rows"] = sum(o.startswith("></think>") for o in outputs)
    out["final_answer_rows"] = sum("<tool_call>" not in o for o in outputs)
    calls = collections.Counter(n for o in outputs for n in CALL.findall(o))
    out["calls_by_tool"] = dict(calls.most_common())
    first = {}
    for r in rows:
        key = (r["meta"]["case_id"], r["meta"]["turn"])
        if r["meta"].get("step") == 1:
            first[key] = r
    out["zero_call_trajectories"] = sum(f["meta"]["traj"]["zero_call"] for f in first.values())
    out["multi_turn_cases"] = len({c for (c, t) in traj if t > 1})
    out["by_batch"] = dict(collections.Counter(r["meta"]["case_tags"].get("family", "").split("-")[2]
                                               if r["meta"]["case_tags"].get("family", "").startswith("fam-nt-b20d")
                                               else "agent" for r in rows))
    tokens = sorted(r["meta"]["traj"]["tokens"] for r in rows)
    out["row_tokens_p50_p99_max"] = [tokens[len(tokens) // 2], tokens[len(tokens) * 99 // 100], tokens[-1]] if tokens else []
    out["row_tokens_total"] = sum(tokens)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--batch", action="append", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    root = Path(REPO)
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    rows, inputs = [], {}
    for batch in args.batch:
        path = root / "local/runs/distill/v20" / batch / "corpus" / "rows.jsonl"
        batch_rows = [json.loads(line) for line in path.read_text().split("\n") if line]
        inputs[str(path.relative_to(root))] = {"rows": len(batch_rows), "sha256": sha(path)}
        rows += batch_rows
    rows = [r if r["text"].endswith(SUFFIX) else add_suffix(r) for r in rows]
    # Per-step rows carry every earlier tool result; a late step after a large
    # read can exceed the trainer context. Drop such rows (each row stands on
    # its own; the trajectory's earlier steps stay). meta.traj.tokens is the
    # World count of the text before the suffix.
    over = [r for r in rows if r["meta"]["traj"]["tokens"] + 8 > MAX_TOKENS]
    rows = [r for r in rows if r["meta"]["traj"]["tokens"] + 8 <= MAX_TOKENS]
    split = {"train": [], "validation": []}
    sides = collections.defaultdict(set)
    for r in rows:
        family = r["meta"]["case_tags"]["family"]
        assert family, r["meta"]["case_id"]
        side = "validation" if int(hashlib.sha256(family.encode()).hexdigest(), 16) % 32 == 0 else "train"
        split[side].append(r)
        sides[family].add(side)
    assert all(len(v) == 1 for v in sides.values())
    out.mkdir(parents=True)
    for side, selected in split.items():
        source = out / (side + "-rows.jsonl")
        source.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in selected))
        dest = out / "dataset" / side
        run(root, out / (side + "-pack.log"), [LAB, "corpus", "pack", "--rows", str(source),
                                               "--max-tokens", str(MAX_TOKENS), "--out", str(dest)])
        run(root, out / (side + "-segments.log"), ["python3", "bench/distill/tools/to_segments.py",
                                                   "--rows", str(dest / "rows.jsonl"), "--out", str(dest / "segments.jsonl")])
        run(root, out / (side + "-segcheck.log"), [LAB, "corpus", "segcheck", str(dest / "segments.jsonl")])
    lines = [l + "\n" for l in (out / "dataset" / "train" / "segments.jsonl").read_text().split("\n") if l]
    order = list(range(len(lines)))
    random.Random(SEED).shuffle(order)
    (out / "dataset" / "train" / "segments-shuffled.jsonl").write_text("".join(lines[i] for i in order))
    stats = {
        "inputs": inputs, "split_method": "sha256(family) mod 32 == 0 -> validation",
        "shuffle_seed": SEED, "dropped_over_max_tokens": len(over), "max_tokens": MAX_TOKENS, "wire_hash": sorted({r["meta"]["wire_hash"] for r in rows}),
        "all": composition(rows), "train": composition(split["train"]),
        "validation": composition(split["validation"]),
        "artifact_sha256": {str(p.relative_to(out)): sha(p) for p in sorted((out / "dataset").glob("*/*")) if p.is_file()},
        "finalizer_sha256": sha(__file__), "lab_sha256": sha(root / LAB),
    }
    (out / "final-stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(stats["all"], ensure_ascii=False))


if __name__ == "__main__":
    main()
