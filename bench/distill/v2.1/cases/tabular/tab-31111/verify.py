# DISTILL-CANARY-a691a1ee : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '35b16cba1dc6ea7f5692f55993484775e0daec6a6bd72710535631fc9b9c4a1f', "fixture changed"
def compute(files):
    d = {}
    for l in files["考勤/9月.csv"].strip().split("\n")[1:]:
        n, _, s = l.split(",")
        if s != "正常":
            d.setdefault(n, {"迟到": 0, "缺勤": 0})[s] += 1
    return {"考勤/异常名单.csv": "姓名,迟到,缺勤\n" + "".join("%s,%d,%d\n" % (n, d[n]["迟到"], d[n]["缺勤"]) for n in sorted(d, key=lambda n: (-(d[n]["迟到"] + d[n]["缺勤"]), n)))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
