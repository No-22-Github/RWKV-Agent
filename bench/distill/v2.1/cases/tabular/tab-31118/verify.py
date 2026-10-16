# DISTILL-CANARY-e8e10aaf : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bc89d92f83d6bcfb3ee94054d2dd1af651d7d63fd7396c3ff718864d9cc73487', "fixture changed"
def compute(files):
    rows = []
    for p, cls in (("成绩/一班.csv", "一班"), ("成绩/二班.csv", "二班")):
        for l in files[p].strip().split("\n")[1:]:
            a, n, s = l.split(",")
            rows.append((cls, n, int(s)))
    rows.sort(key=lambda r: (-r[2], r[1]))
    return {"成绩/总榜.csv": "名次,班级,姓名,分数\n" + "".join("%d,%s,%s,%d\n" % (i + 1, r[0], r[1], r[2]) for i, r in enumerate(rows))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
