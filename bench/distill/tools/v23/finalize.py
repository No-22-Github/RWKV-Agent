#!/usr/bin/env python3
"""Pack the v2.3 per-step g1k-think rows (agent-tool-v3.2) into a MiSS training set.

    python3 bench/distill/tools/v23/finalize.py --batch b22a [--batch ...] \
        --rows local/runs/distill/v21-v3/kept/main.jsonl [--rows ...] \
        --drop-trajectories local/runs/distill/v21-v3/boundary-drop.txt \
        [--concept-cap 80] --out local/runs/distill/v2.3/final-<date>

Copied from tools/v21/finalize.py. Inputs: local/runs/distill/v2.3/<batch>/corpus/rows.jsonl
(render.sh / render_pick.sh output) and any --rows file (the v2.1 rows kept by
the agent-tool-v3.2 replay). --drop-trajectories takes boundary-drop.txt lines
("<input>\t<case_id>#<turn>"); those turns' rows are dropped before anything
else (v2.2 plan §3). The context default is 16K (user decision 10-19).
Concept questions (scenario notool, task_type concept) are capped at
--concept-cap trajectories: cases sorted by sha256(case id), whole cases kept
while the running trajectory count fits.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v21"))
from scan_forbidden import bad as forbidden_call  # noqa: E402

LAB = "local/bin/rwkv-lab-v23"
SEED = 20261030
MAX_TOKENS = 16320
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
    out["trajectories_by_source"] = dict(collections.Counter(r["meta"]["source"] for r in first.values()))
    out["concept_trajectories"] = sum(is_concept(f) for f in first.values())
    out["zh_trajectories"] = sum(bool(CJK.search(f["text"].rsplit("\n\nUser: ", 1)[-1][:400])) for f in first.values())
    tokens = sorted(r["meta"]["traj"]["tokens"] for r in rows)
    out["row_tokens_p50_p99_max"] = [tokens[len(tokens) // 2], tokens[len(tokens) * 99 // 100], tokens[-1]] if tokens else []
    out["row_tokens_total"] = sum(tokens)
    return out


def is_concept(row):
    tags = row["meta"]["case_tags"]
    return tags.get("scenario") == "notool" and tags.get("task_type") == "concept"


def cap_concept(rows, cap):
    traj = collections.defaultdict(set)
    for r in rows:
        if is_concept(r):
            traj[r["meta"]["case_id"]].add(r["meta"]["turn"])
    keep, n = set(), 0
    for cid in sorted(traj, key=lambda c: hashlib.sha256(c.encode()).hexdigest()):
        if n + len(traj[cid]) <= cap:
            keep.add(cid)
            n += len(traj[cid])
    return [r for r in rows if not is_concept(r) or r["meta"]["case_id"] in keep], len(traj) - len(keep)


def cap_source(rows, share):
    """Whole cases (by sha256 of the id) leave an over-represented source until
    its trajectories fit share x total (v2.3 plan §5: one source <= 25%)."""
    traj = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        traj[r["meta"]["source"]][r["meta"]["case_id"]].add(r["meta"]["turn"])
    total = sum(len(t) for cases in traj.values() for t in cases.values())
    dropped = {}
    for source, cases in traj.items():
        n = sum(len(t) for t in cases.values())
        out = set()
        for cid in sorted(cases, key=lambda c: hashlib.sha256(c.encode()).hexdigest()):
            if n - sum(len(cases[c]) for c in out) <= share * (total - 0):
                break
            out.add(cid)
        if out:
            dropped[source] = sorted(out)
    gone = {c for v in dropped.values() for c in v}
    return [r for r in rows if r["meta"]["case_id"] not in gone], {k: len(v) for k, v in dropped.items()}


def balance(rows):
    """v2.3 plan §5 targets, per trajectory (case#turn) unless noted."""
    first, traj = {}, collections.defaultdict(list)
    for r in rows:
        key = (r["meta"]["case_id"], r["meta"]["turn"])
        traj[key].append(r)
        if r["meta"].get("step") == 1:
            first[key] = r
    n = len(traj)
    case_turns = collections.Counter(c for c, _ in traj)
    scen = collections.Counter(r["meta"]["case_tags"].get("scenario") for r in first.values())
    local = [f for f in first.values() if f["meta"]["case_tags"].get("scenario") not in ("web", "hybrid", "notool")]
    refusal = {k for k, v in traj.items() if not any(r["meta"].get("step") == 1 for r in v)}
    calls = {k: max(r["meta"]["traj"]["tool_calls"] for r in v) for k, v in traj.items()}
    sources = collections.Counter(r["meta"]["source"] for v in traj.values() for r in v[:1])
    pct = lambda a, b: round(100.0 * a / b, 1) if b else 0.0
    table = {
        "trajectories (1900-2200)": n,
        "scenario share % (6-16; script >=2)": {k: pct(v, len(first)) for k, v in scen.most_common()},
        "zero-call % (18-22)": pct(sum(f["meta"]["traj"]["zero_call"] for f in first.values()), len(first)),
        "zh % (50-58)": pct(sum(bool(CJK.search(f["text"].rsplit("\n\nUser: ", 1)[-1][:400])) for f in first.values()), len(first)),
        "multi-turn cases % (>=30)": pct(sum(t > 1 for t in case_turns.values()), len(case_turns)),
        "cases with >=3 user turns (>=70)": len({c for c, t in traj if t >= 3}),
        "clarify trajectories (>=60)": sum(1 for f in first.values() if f["meta"].get("kind") == "clarify"
                                          or "b23c" in f["meta"]["source"]),
        "refusal-constructed trajectories (250-320, <=15%)": [len(refusal), pct(len(refusal), n)],
        ">=8 tool calls % (<=2)": pct(sum(v >= 8 for v in calls.values()), n),
        "local-scenario first web_search % (<=1)": pct(sum((f["meta"]["traj"].get("tool_seq") or [""])[0] == "web_search" for f in local), len(local)),
        "largest source % (<=25)": [sources.most_common(1)[0][0], pct(sources.most_common(1)[0][1], n)] if sources else [],
    }
    return table


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--batch", action="append", default=[])
    ap.add_argument("--rows", action="append", default=[], type=Path)
    ap.add_argument("--drop-trajectories", type=Path, help="boundary-drop.txt: <input>\\t<case_id>#<turn> per line")
    ap.add_argument("--drop-cases", type=Path, help="v2.3: <case_id>\\t<reasons> per line; every turn of the case is dropped")
    ap.add_argument("--step1-only", type=Path, help="v2.3: JSON list of case ids (16K-repaired old paths); trajectories "
                    "with more than 3 tool calls keep only their step-1 row, as in the v2.1 8K pack")
    ap.add_argument("--source-cap", type=float, default=0.25, help="v2.3: max share of trajectories from one source")
    ap.add_argument("--concept-cap", type=int, default=80)
    ap.add_argument("--max-tokens", type=int, default=MAX_TOKENS, help="trainer context minus the suffix margin")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    root = Path(REPO)
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    rows, inputs = [], {}
    paths = [root / "local/runs/distill/v2.3" / b / "corpus" / "rows.jsonl" for b in args.batch]
    for path in paths + [p.resolve() for p in args.rows]:
        batch_rows = [json.loads(line) for line in path.read_text().split("\n") if line]
        inputs[str(path.relative_to(root))] = {"rows": len(batch_rows), "sha256": sha(path)}
        rows += batch_rows
    boundary = set()
    if args.drop_trajectories:
        for line in args.drop_trajectories.read_text().split("\n"):
            if line.strip():
                case_id, turn = line.split("\t")[1].rsplit("#", 1)
                boundary.add((case_id, int(turn)))
    before = len(rows)
    rows = [r for r in rows if (r["meta"]["case_id"], r["meta"]["turn"]) not in boundary]
    boundary_rows = before - len(rows)
    drop_cases = set()
    if args.drop_cases:
        drop_cases = {l.split("\t")[0] for l in args.drop_cases.read_text().split("\n") if l.strip()}
    rows = [r for r in rows if r["meta"]["case_id"] not in drop_cases]
    step1 = set(json.loads(args.step1_only.read_text())) if args.step1_only else set()
    demoted = {(r["meta"]["case_id"], r["meta"]["turn"]) for r in rows
               if r["meta"]["case_id"] in step1 and r["meta"]["traj"]["tool_calls"] > 3}
    rows = [r for r in rows if (r["meta"]["case_id"], r["meta"]["turn"]) not in demoted or r["meta"]["step"] == 1]
    rows, source_capped = cap_source(rows, args.source_cap)
    ids = collections.Counter(r["meta"]["case_id"] for r in rows if r["meta"].get("step") == 1 and r["meta"]["turn"] == 1)
    assert max(ids.values()) == 1, [c for c, n in ids.items() if n > 1][:5]
    rows, concept_dropped = cap_concept(rows, args.concept_cap)
    # A tool call trained right after the harness disabled the tools is the
    # closeout failure this round fixes; drop that whole turn.
    forbidden = {(r["meta"]["case_id"], r["meta"]["turn"]) for r in rows if forbidden_call(r)}
    rows = [r for r in rows if (r["meta"]["case_id"], r["meta"]["turn"]) not in forbidden]
    rows = [r if r["text"].endswith(SUFFIX) else add_suffix(r) for r in rows]
    # Per-step rows carry every earlier tool result; a late step after a large
    # read can exceed the trainer context. Drop such rows (each row stands on
    # its own; the trajectory's earlier steps stay). meta.traj.tokens is the
    # World count of the text before the suffix.
    over = [r for r in rows if r["meta"]["traj"]["tokens"] + 8 > args.max_tokens]
    rows = [r for r in rows if r["meta"]["traj"]["tokens"] + 8 <= args.max_tokens]
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
                                               "--max-tokens", str(args.max_tokens), "--out", str(dest)])
        run(root, out / (side + "-segments.log"), ["python3", "bench/distill/tools/to_segments.py",
                                                   "--rows", str(dest / "rows.jsonl"), "--out", str(dest / "segments.jsonl")])
        run(root, out / (side + "-segcheck.log"), [LAB, "corpus", "segcheck", str(dest / "segments.jsonl")])
    lines = [l + "\n" for l in (out / "dataset" / "train" / "segments.jsonl").read_text().split("\n") if l]
    order = list(range(len(lines)))
    random.Random(SEED).shuffle(order)
    (out / "dataset" / "train" / "segments-shuffled.jsonl").write_text("".join(lines[i] for i in order))
    stats = {
        "inputs": inputs, "split_method": "sha256(family) mod 32 == 0 -> validation",
        "shuffle_seed": SEED, "boundary_trajectories_dropped": len(boundary), "boundary_rows_dropped": boundary_rows, "dropped_over_max_tokens": len(over), "concept_cases_dropped": concept_dropped, "forbidden_call_turns_dropped": sorted("%s#%d" % k for k in forbidden), "concept_cap": args.concept_cap, "max_tokens": args.max_tokens, "wire_hash": sorted({r["meta"]["wire_hash"] for r in rows}),
        "drop_cases": len(drop_cases), "step1_only_trajectories": len(demoted), "source_capped_cases": source_capped,
        "balance": balance(rows),
        "all": composition(rows), "train": composition(split["train"]),
        "validation": composition(split["validation"]),
        "artifact_sha256": {str(p.relative_to(out)): sha(p) for p in sorted((out / "dataset").glob("*/*")) if p.is_file()},
        "finalizer_sha256": sha(__file__), "lab_sha256": sha(root / LAB),
    }
    (out / "final-stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(stats["all"], ensure_ascii=False))
    print(json.dumps(stats["balance"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
