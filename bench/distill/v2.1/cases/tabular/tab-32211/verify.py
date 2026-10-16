# DISTILL-CANARY-db4b523b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a6ec7f2e6b7babdd7d79a55ccbcda38ae92eaf72d93006e4a28056721830e658', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["sensors/readings.jsonl"].splitlines()]
    ok = [r for r in rows if r.get("valid") is True]
    m = max(r["temp_c"] for r in ok)
    devs = sorted({r["device"] for r in ok if r["temp_c"] == m})
    assert len(devs) == 1
    allm = max(r["temp_c"] for r in rows)
    return {"turns": [{"number": m, "items": devs}], "decoys": {"TR-DECOY": allm, "TR-MISSING": max(r["temp_c"] for r in rows if r.get("valid") is not False)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
