#!/usr/bin/env python3
"""b09 follow-up (v1.4 §3.8, §3.9): drop hard mental-arithmetic rows, then cap b05 per family.

Run after `v14_rewrite_finals.py apply` and the b09 render. Rows are judged the
way pack sees them: v1.3 train/val rows plus the b09 render, minus every row
exclude.jsonl already strikes (an entry only strikes rows of its own batch).

  v14_m1_closeout.py [--dry-run] [--stats out.json]
"""
import argparse
import itertools
import json
import os
import re
from collections import Counter, defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EXCLUDE_JSONL = os.path.join(REPO, "bench", "distill", "exclude.jsonl")
V13_ROWS = [os.path.join(REPO, "local", "runs", "distill", "v13-clean", f) for f in ("train-rows.jsonl", "val-rows.jsonl")]
B09_ROWS = os.path.join(REPO, "local", "runs", "distill", "v14", "b09", "rows.jsonl")
B09_TASKS = os.path.join(REPO, "bench", "distill", "b09_work", "all_tasks.json")
FAMILY_CAP = 3
CAP_HALT = 250

NUM = re.compile(r'(?<![\w.])-?\d+(?:,\d{3})*(?:\.\d+)?(?![\w])')


def load_excludes():
    ex = defaultdict(set)
    for line in open(EXCLUDE_JSONL):
        e = json.loads(line)
        ex[e["case_id"]].add(e.get("batch", ""))
    return ex


def batch_of(meta):
    return meta.get("source", "").removeprefix("distill-")


def struck(ex, meta):
    b = ex.get(meta["case_id"])
    return bool(b) and ("" in b or not meta.get("source") or batch_of(meta) in b)


def final_text(row):
    s, e = row["loss_spans"][-1]
    return row["text"][s:e]


def numeric_value(text):
    """A final answer that is a number, optionally with currency or a short unit."""
    s = re.sub(r'^[£$€¥]', '', text.replace("\n\nUser:", "").strip())
    m = re.fullmatch(r'(-?\d+(?:,\d{3})*(?:\.\d+)?)(?:\s*[A-Za-z% ]{0,30})?', s)
    return float(m.group(1).replace(",", "")) if m else None


def easy_op(result, operands):
    """One step a person does in their head: +/- of integers ≤100, a times-table
    product (one factor ≤12, other ≤100), or exact division by ≤12 of ≤1000."""
    for a, b in itertools.permutations(operands, 2):
        if not (a.is_integer() and b.is_integer()):
            continue
        for op in "+-*/":
            x = a + b if op == "+" else a - b if op == "-" else a * b if op == "*" else (a / b if b else None)
            if x is None or abs(x - result) > 1e-9 * max(1, abs(result)):
                continue
            if op in "+-" and abs(a) <= 100 and abs(b) <= 100:
                return f"{a:g}{op}{b:g}"
            if op == "*" and min(abs(a), abs(b)) <= 12 and max(abs(a), abs(b)) <= 100:
                return f"{a:g}{op}{b:g}"
            if op == "/" and 0 < abs(b) <= 12 and abs(a) <= 1000 and x.is_integer():
                return f"{a:g}{op}{b:g}"
    return None


def mental_arithmetic(row, value_text):
    """None when the row is not mental arithmetic under an offered calculator,
    else ("easy", op) or ("hard", "")."""
    meta, text = row["meta"], row["text"]
    if not meta["traj"]["zero_call"]:
        return None
    if "calculator" not in text[: text.find("\n\nUser:")]:
        return None
    s = row["loss_spans"][-1][0]
    context = text[text.find("\n\nUser:"): s]
    v = numeric_value(value_text)
    if v is None:
        return None
    seen = {float(n.replace(",", "")) for n in NUM.findall(context)}
    if v in seen or v in (0, 1, 2):
        return None  # read off the context, not computed
    operands = sorted((o for o in seen if abs(o) < 1e7), key=abs)[:400]
    op = easy_op(v, operands)
    return ("easy", op) if op else ("hard", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--stats")
    args = ap.parse_args()

    ex = load_excludes()
    # b09 finals are sentences; judge them on the value they were rewritten from.
    b09_value = {}
    for t in json.load(open(B09_TASKS)):
        b09_value.setdefault(t["case_id"], t["original_value"])

    rows = []
    for path in V13_ROWS + [B09_ROWS]:
        for line in open(path):
            r = json.loads(line)
            if not struck(ex, r["meta"]):
                rows.append(r)

    # §3.8 M8
    m8 = []
    m8_easy = []
    for r in rows:
        meta = r["meta"]
        value = b09_value.get(meta["case_id"].split("--")[0]) if batch_of(meta) == "b09" else final_text(r)
        verdict = mental_arithmetic(r, value or "")
        if verdict is None:
            continue
        item = {"case_id": meta["case_id"], "batch": batch_of(meta), "turn": meta["turn"], "value": value.strip()[:40], "op": verdict[1]}
        (m8 if verdict[0] == "hard" else m8_easy).append(item)
    # exclude.jsonl strikes a whole path, so one hard turn takes the path with it.
    m8 = list({(i["case_id"], i["batch"]): i for i in m8}.values())
    m8_ids = {(i["case_id"], i["batch"]) for i in m8}
    rows = [r for r in rows if (r["meta"]["case_id"], batch_of(r["meta"])) not in m8_ids]

    # §3.9 family cap: count every kept row; only b05 rows are dropped, keeping
    # b09 rewrites first, then --p81 closeout rows, then b05 in path order.
    def rank(r):
        b = batch_of(r["meta"])
        return (0 if b == "b09" else 1 if r["meta"]["case_id"].endswith("--p81") else 2, r["meta"]["case_id"], r["meta"]["turn"])

    by_family = defaultdict(list)
    for r in rows:
        by_family[r["meta"]["case_tags"].get("family", "unknown")].append(r)
    cap = []
    cap_kind = Counter()
    over_after = []
    for fam, rs in sorted(by_family.items()):
        rs.sort(key=rank)
        drop = [r for r in rs[FAMILY_CAP:] if batch_of(r["meta"]) == "b05"]
        dropped_ids = {r["meta"]["case_id"] for r in drop}
        # A path is excluded whole, so every turn row of it goes.
        drop_rows = [r for r in rs if batch_of(r["meta"]) == "b05" and r["meta"]["case_id"] in dropped_ids]
        # §3.9 caps the b05 stock; families made only of b06/b07 rows are out of scope.
        if any(batch_of(r["meta"]) == "b05" for r in rs) and len(rs) - len(drop_rows) > FAMILY_CAP:
            over_after.append(fam)
        for cid in sorted(dropped_ids):
            cap.append(cid)
        for r in drop_rows:
            cap_kind[r["meta"].get("kind", "unknown")] += 1

    stats = {
        "m8_hard": len(m8), "m8_hard_by_batch": dict(Counter(i["batch"] for i in m8)),
        "m8_easy_kept": len(m8_easy), "m8_easy_examples": m8_easy[:10],
        "cap_paths": len(cap), "cap_rows": sum(cap_kind.values()), "cap_rows_by_kind": dict(cap_kind),
        "b05_families_over_cap_after": over_after,
    }
    print(json.dumps(stats, ensure_ascii=False, indent=1))
    if args.stats:
        json.dump({**stats, "m8_hard_items": m8, "m8_easy_items": m8_easy, "cap_case_ids": cap},
                  open(args.stats, "w"), ensure_ascii=False, indent=1)
    if stats["cap_rows"] > CAP_HALT:
        raise SystemExit(f"family cap would drop {stats['cap_rows']} rows > {CAP_HALT}; halting per §3.9")
    if args.dry_run:
        return

    with open(EXCLUDE_JSONL, "a", encoding="utf-8") as f:
        for i in m8:
            f.write(json.dumps({"batch": i["batch"], "case_id": i["case_id"], "reason": "v1.4 M8 心算"}, ensure_ascii=False) + "\n")
        for cid in cap:
            f.write(json.dumps({"batch": "b05", "case_id": cid, "reason": "v1.4 family 封顶"}, ensure_ascii=False) + "\n")
    print(f"Appended {len(m8)} M8 + {len(cap)} cap exclusions to {EXCLUDE_JSONL}")


if __name__ == "__main__":
    main()
