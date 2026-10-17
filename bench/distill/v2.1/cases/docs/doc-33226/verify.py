# DISTILL-CANARY-177e463b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9e8d668746935479dd673ea207132d5aaa36723e9692c5db5fb176f1aa065254', "fixture changed"
files = case["files"]
def compute(files):
    out = ""
    for l in files["论文/参考文献.txt"].strip().split("\n"):
        parts = l.split(". ")
        year = int(parts[-1].rstrip(".").split(", ")[-1])
        if year >= 2020:
            out += "%s,%d\n" % (parts[1], year)
    return {"论文/近五年.csv": "题目,年份\n" + out}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
