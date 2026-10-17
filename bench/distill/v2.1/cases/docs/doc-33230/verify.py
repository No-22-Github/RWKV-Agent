# DISTILL-CANARY-2cac7a51 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a4165c4515ae965f2608db4ebbc7223d58fb5720cf848aa7031cc0410de97d21', "fixture changed"
files = case["files"]
def compute(files):
    rows = []
    for l in files["客服/反馈汇总.txt"].strip().split("\n"):
        if "[投诉]" in l:
            rows.append("%s,%s" % (l.split(" ")[0], l.split("] ", 1)[1]))
    return {"客服/投诉.csv": "订单号,问题\n" + "".join(r + "\n" for r in rows)}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
