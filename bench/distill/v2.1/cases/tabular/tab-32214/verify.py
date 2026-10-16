# DISTILL-CANARY-65e06ea2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6baabee213cd894b903cf5f3aee65ed85f19085fbbc279879976dc6ea3f77adc', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["trace/spans.jsonl"].splitlines()]
    tot = sum(len(r.get("errors") or []) for r in rows)
    lines = sum(1 for r in rows if r.get("errors"))
    return {"turns": [{"number": tot, "items": []}, {"number": lines, "items": []}], "decoys": {"TR-MISSING": len(rows), "TR-DECOY": lines}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
