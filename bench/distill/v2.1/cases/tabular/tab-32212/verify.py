# DISTILL-CANARY-a7b01652 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '49010df46b351dba02ea2416cca45f58db1e8393bb0856010b55d232ec669415', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["成绩/records.jsonl"].splitlines()]
    d = {}
    for r in rows:
        d.setdefault(r["student"], []).append(r["score"])
    a = [s for s, v in d.items() if len(v) >= 2 and sum(v) / len(v) >= 85]
    b = [s for s, v in d.items() if sum(v) / len(v) >= 85]
    return {"turns": [{"number": len(a), "items": []}], "decoys": {"TR-DEFN": len(b), "TR-DUPROW": len(d)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
