# DISTILL-CANARY-b8a78110 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a09c6ad9e3f7f319a975ae3a415fc1ea3eec237adf460359441a61469c4e2a05', "fixture changed"
def compute(files):
    d = {}
    for l in files["设备/温度.csv"].strip().split("\n")[1:]:
        _, r, t = l.split(",")
        d.setdefault(r, []).append(float(t))
    out = "机房,最高,最低,平均\n"
    for r in sorted(d):
        v = d[r]
        out += "%s,%.1f,%.1f,%.1f\n" % (r, max(v), min(v), sum(v) / len(v))
    return {"设备/机房统计.csv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
