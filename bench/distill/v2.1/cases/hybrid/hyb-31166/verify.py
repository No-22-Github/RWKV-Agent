# DISTILL-CANARY-ffe1b4f5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6588ec423409b2453b9a7e8b69f269c565d2376ca03fa5a6b27af7c441cc9698', "fixture changed"
def compute(files):
    return {"协议/摘要.txt": "合同摘要\n甲方：北辰科技\n乙方：南岸咨询\n金额：50000\n期限：12\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
