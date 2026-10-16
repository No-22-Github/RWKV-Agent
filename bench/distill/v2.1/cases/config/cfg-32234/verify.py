# DISTILL-CANARY-069f5f8a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '19e893fa39ff935e163d7a39da379a265cb564d415b3c36c5116c6e905d2461c', "fixture changed"
import re
def solve(files):
    n = 0
    for t in files.values():
        sec = None
        for l in t.splitlines():
            if l.startswith("["):
                sec = l
            elif sec == "[db]" and l.startswith("port=") and l != "port=5432":
                n += 1
    al = len([1 for t in files.values() for l in t.splitlines() if l.startswith("port=") and l != "port=5432"])
    return {"turns": [{"number": n, "items": []}], "decoys": {"TR-DECOY": al, "TR-TRUNC": 50}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
