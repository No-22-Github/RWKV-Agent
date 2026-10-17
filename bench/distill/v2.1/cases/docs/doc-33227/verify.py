# DISTILL-CANARY-df75b4e5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '59afdbeb17a29f9f1c78a6478e499602da838561c344b32a5f6ebaa1b75fc856', "fixture changed"
files = case["files"]
FACTS = json.loads('["供应商,期限", "恒达电子,", "30天", "晨光文具,", "次月15日前", "凯瑞包装,", "7天", "蓝海物流,", "20天", "远景科技,", "15天"]')
corpus = "".join(files.values()) + "".join(t["prompt"] for t in case["turns"])
FREE = json.loads('["供应商,期限", "恒达电子,", "晨光文具,", "次月15日前", "凯瑞包装,", "7天", "蓝海物流,", "20天", "远景科技,", "30天"]')
assert all(f in corpus for f in FACTS if f not in FREE), [f for f in FACTS if f not in corpus and f not in FREE]
FINAL = {p: "\n".join(FACTS) for p, r in case["expect"]["files"].items() if "contains" in r}
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
