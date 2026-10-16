# DISTILL-CANARY-cc89acee : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'de654734c9f280c1b7b7f8f424fae608b73a175245758e15435f1adbbd46b2e0', "fixture changed"
import re
def solve(files):
    hit = {}
    for p, t in files.items():
        if re.search(r"^LOG_LEVEL=debug$", t, re.M):
            hit[p.split("/")[1]] = hit.get(p.split("/")[1], 0) + 1
    r = sorted(hit.items(), key=lambda kv: -kv[1])
    assert r[0][1] > r[1][1]
    return {"turns": [{"number": sum(hit.values()), "items": []}, {"number": r[0][1], "items": [r[0][0]]}],
            "decoys": {"TR-DECOY": len([1 for t in files.values() if "LOG_LEVEL=debug" in t]), "TR-TRUNC": 50}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
