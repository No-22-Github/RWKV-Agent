# DISTILL-CANARY-fe459db6 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["配置/说明.md"].startswith("票价按场次")
prices = {}
for tier in ("工作日日场", "周末日场", "夜场"):
    m = re.search(r"票价元:\s*(\d+)", f["配置/票价/%s.yaml" % tier])
    assert m, tier
    prices[tier] = int(m.group(1))
chosen = [t for t in ("工作日日场", "周末日场", "夜场") if t in case["turns"][1]["prompt"]]
assert len(chosen) == 2, chosen
ask = ["哪两个场次", "哪几个场次", "哪两场", "哪些场次", "场次的名称", "场次名称", "场次编号"]
print(json.dumps({"expected_number": prices["工作日日场"], "expected_contains_any": ask}, ensure_ascii=False))
