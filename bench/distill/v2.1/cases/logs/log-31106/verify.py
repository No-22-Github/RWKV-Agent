# DISTILL-CANARY-c2428ea6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3023383cc9eaa01b7e8ec04e34c379b9de866d692875ce8b3ee0068cac72d121', "fixture changed"
def compute(files):
    import json
    d = {}
    for l in files["监控/请求.jsonl"].strip().split("\n"):
        r = json.loads(l)
        d.setdefault(r["path"], []).append(r["ms"])
    return {"监控/耗时.json": json.dumps({k: {"count": len(v), "avg_ms": sum(v) // len(v)} for k, v in sorted(d.items())}, indent=2) + "\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
