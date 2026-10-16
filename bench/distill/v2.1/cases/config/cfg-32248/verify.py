# DISTILL-CANARY-d35ad707 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '40129b5f6964b94a2d31a5679fb9950df042cb7057e17fd9389b5f2e835f776c', "fixture changed"
import re
def solve(files):
    d = sorted(t.splitlines()[0].split(": ")[1] for p, t in files.items() if p.endswith(".yaml") and "enabled: false" in t.splitlines())
    return {"turns": [{"number": len(d), "items": []}], "files": {"svc/disabled.txt": "".join(x + "\n" for x in d)}, "decoys": {}}

ans = solve(case["files"])
print(json.dumps({"files": ans["files"]}, ensure_ascii=False))
