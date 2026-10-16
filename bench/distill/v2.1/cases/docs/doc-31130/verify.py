# DISTILL-CANARY-8f4707b4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0d28d073453274bcdb4a40cbd8434fe2cf2a8dcbbcd6f267b878fc4a324eaa31', "fixture changed"
def compute(files):
    out = "星期,时间,课程\n"
    for p, d in (("课表/周一.txt", "周一"), ("课表/周二.txt", "周二")):
        for l in files[p].strip().split("\n"):
            t, c = l.split()
            out += "%s,%s,%s\n" % (d, t, c)
    return {"课表/总课表.csv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
