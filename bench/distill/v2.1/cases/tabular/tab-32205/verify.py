# DISTILL-CANARY-8d58e64b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a8ced6d0889ecff5fb910505eb25c93d84c951bb5a6eb102f96f937c9c82c278', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["埋点/events.jsonl"].splitlines()]
    p = [r for r in rows if r["event"] == "purchase"]
    a = {r["user"] for r in p}
    b = {r["user"] for r in p if (r.get("props") or {}).get("region") == "华东"}
    return {"turns": [{"number": len(a), "items": []}, {"number": len(b), "items": []}], "decoys": {"TR-DUPROW": len(p), "TR-MISSING": len({r["user"] for r in p if r.get("props")})}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
