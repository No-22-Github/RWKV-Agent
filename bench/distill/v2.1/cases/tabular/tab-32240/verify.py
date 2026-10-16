# DISTILL-CANARY-7856f6d4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'edaf3cfd7b53b13378be8f907864632e8a6e8b59a1d41aab96eb5dd26a8f1431', "fixture changed"
import re
def solve(files):
    o = json.loads(files["price/old.json"])
    n = json.loads(files["price/new.json"])
    ch = sorted(k for k in o if k in n and o[k] != n[k])
    ad = sorted(set(n) - set(o))
    return {"turns": [{"number": len(ch), "items": []}, {"number": len(ad), "items": ad}], "decoys": {"TR-DECOY": len(ch) + len(ad)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
