# DISTILL-CANARY-1212569f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'dc1e003922850c9c34acc35b6e3bc0c3109bb0a6e0f5d7765f17c92fb779716a', "fixture changed"
def compute(files):
    rows = [l.split(",") for l in files["客户/档案.csv"].strip().split("\n")[1:]]
    sh = [r for r in rows if r[2] == "上海"]
    return {"客户/上海.csv": "id,公司\n" + "".join("%s,%s\n" % (r[0], r[1]) for r in sh), "客户/其他.csv": "id,公司,城市\n" + "".join(",".join(r) + "\n" for r in rows if r[2] != "上海")}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
