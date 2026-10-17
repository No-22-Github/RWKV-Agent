# DISTILL-CANARY-a67766b6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a14be67f18cce92bc93878c4118bbb56405e4c4aa48307f48ea1187ba99a9462', "fixture changed"
files = case["files"]
def compute(files):
    dept, rows = "", []
    for l in files["通讯录/内部.txt"].split("\n"):
        if l and not l.startswith(" "):
            dept = l
        elif l:
            n, p = l.split()
            if dept != "市场部":
                rows.append("%s,%s,%s" % (n, p, dept))
    return {"通讯录/联系人.csv": "姓名,电话,部门\n" + "\n".join(rows) + "\n"}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
