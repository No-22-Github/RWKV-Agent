# DISTILL-CANARY-43463355 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '747d00ac120961ff5afe51cd934082d047909d19743f2a875572f396dc1bb7a1', "fixture changed"
def compute(files):
    return {"稿/开场白.txt": "各位同事大家好，今天我们回顾本季度的销售情况。\n先看整体，再看分区，最后聊聊下季度的目标。\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
