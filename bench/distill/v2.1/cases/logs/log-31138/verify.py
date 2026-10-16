# DISTILL-CANARY-c169d74d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '70729f02cfe2b941222f5d904ee6a8d350286e001e8054be5bcc229e1af62c6d', "fixture changed"
def compute(files):
    d = {}
    for l in files["访客/记录.log"].strip().split("\n"):
        _, n, _ = l.split()
        d[n] = d.get(n, 0) + 1
    return {"访客/统计.txt": "".join("%s=%d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
