# DISTILL-CANARY-352d101e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0d01b1bd64e03d2bbe88e52d09dd302445d52a4dca1374f1e1bb5999964bb56d', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["iot/events.jsonl"].splitlines()]
    err, tot = {}, {}
    for r in rows:
        tot[r["device"]] = tot.get(r["device"], 0) + 1
        if r["event"].get("level") == "error":
            err[r["device"]] = err.get(r["device"], 0) + 1
    er = sorted(err.items(), key=lambda kv: -kv[1])
    to = sorted(tot.items(), key=lambda kv: -kv[1])
    assert er[0][1] > er[1][1] and to[0][0] != er[0][0]
    return {"turns": [{"number": er[0][1], "items": [er[0][0]]}], "decoys": {"TR-DECOY": to[0][1], "TR-MISSING": er[1][1]}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
