# DISTILL-CANARY-c7ce4de4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '773054246c021d7910bfa258b03063412f4d8b104e049a1e26ead40ad04b53bb', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["edge/access-0914.jsonl"].splitlines()]
    a = [r for r in rows if r["path"] == "/v2/checkout" and r["status"] >= 500]
    b = [r for r in a if r.get("latency_ms") is not None and r["latency_ms"] > 800]
    c = [r for r in rows if r["path"].startswith("/v2/checkout") and r["status"] >= 500]
    return {"turns": [{"number": len(a), "items": []}, {"number": len(b), "items": []}], "decoys": {"TR-DECOY": len(c), "TR-MISSING": len([r for r in a if "latency_ms" in r])}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
