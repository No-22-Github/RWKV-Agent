# DISTILL-CANARY-fae9f998 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e9d1573cea6a07f80e02684946d27f0a7bdfc39b98df18796c5fb76e95d166a1', "fixture changed"
import re
def solve(files):
    hits = [(p, n + 1) for p, t in files.items() for n, l in enumerate(t.splitlines()) if re.search(r"ORDER-7731(?!\d)", l)]
    assert len(hits) == 1
    return {"turns": [{"number": hits[0][1], "items": [hits[0][0].split("/")[1]]}], "decoys": {"TR-DECOY": len([1 for p, t in files.items() if "ORDER-7731" in t]), "TR-TRUNC": 50}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
