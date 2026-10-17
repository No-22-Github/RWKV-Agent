# DISTILL-CANARY-4351e4d4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0fb0ca557135ed81e6542285c633d9b59a19107344f76c5a7e05c76ce9eba7d6', "fixture changed"
files = case["files"]
def compute(files):
    rows = [l.split(",") for l in files["设备/清单.csv"].strip().split("\n")[1:]]
    rows = [r for r in rows if r[2] <= "2026-12-31"]
    rows.sort(key=lambda r: r[2])
    return {"设备/即将到期.csv": "设备,编号,保修到期,状态\n" + "".join("%s,%s,%s,待续保\n" % tuple(r) for r in rows)}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
