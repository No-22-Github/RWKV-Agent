# DISTILL-CANARY-a84203c5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'de1836accb27c86140525b0bf8c29b5a1168427eb93d86b2fa7f21b64de91c91', "fixture changed"
import re
def solve(files):
    s = sorted(json.loads(t)["name"] for p, t in files.items() if p.endswith(".json") and json.loads(t)["timeout_ms"] > 1000)
    return {"turns": [{"number": len(s), "items": []}, {"number": len(s), "items": []}], "files": {"配置/slow.txt": "".join(x + "\n" for x in s)}, "decoys": {"TR-LONG": 50}}

ans = solve(case["files"])
print(json.dumps({"files": ans["files"]}, ensure_ascii=False))
