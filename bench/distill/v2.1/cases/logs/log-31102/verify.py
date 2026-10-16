# DISTILL-CANARY-cc6553e9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2f567717ba93d156f24b629bb2ee0fc6da4672c1c402a56f94ee0440102e3d00', "fixture changed"
def compute(files):
    c = {}
    for l in files["日志/app.log"].strip().split("\n"):
        p = l.split(" ", 3)
        if p[2] == "ERROR":
            c[p[3]] = c.get(p[3], 0) + 1
    return {"日志/错误统计.txt": "".join("%s: %d\n" % (k, c[k]) for k in sorted(c, key=lambda k: (-c[k], k)))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
