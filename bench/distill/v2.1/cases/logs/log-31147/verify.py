# DISTILL-CANARY-6e224db1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f0a29d6162682cabfc90c61f4d7a2f55ff99924804839b4855173b65c5418f1f', "fixture changed"
def compute(files):
    ls = [l.split(" ", 3) for l in files["故障/事件.log"].strip().split("\n")]
    db = [l for l in ls if l[1] == "DB"]
    mins = sum(int(l[3][2:-2]) for l in db)
    return {"故障/复盘.md": "# 故障复盘\n\n## DB 相关\n" + "".join("- %s %s\n" % (l[0], l[2]) for l in db) + "\n共 %d 分钟\n" % mins}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
