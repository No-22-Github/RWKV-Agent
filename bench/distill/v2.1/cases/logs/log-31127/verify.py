# DISTILL-CANARY-165d3f8f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd54e57b2a7623a6021e8b3dabd3d3cbc32cb7f39790958a5c232ad732156a770', "fixture changed"
def compute(files):
    out = "time,event,user\n"
    for l in files["日志/events.log"].strip().split("\n"):
        t, e, u = l.split()
        out += "%s,%s,%s\n" % (t.split("T")[1], e.upper(), u.capitalize())
    return {"日志/events.csv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
