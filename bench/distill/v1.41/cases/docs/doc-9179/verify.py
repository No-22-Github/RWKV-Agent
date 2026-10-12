# DISTILL-CANARY-a414768a : distillation case
import json
case = json.load(open("case.json"))
LINES = {'docs/发布流程.md': 4, 'docs/发布流程-旧版.md': 3}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
text = case["files"]["docs/发布流程.md"]
assert text.startswith("# 发布流程")
assert "上线前需要 3 位审批人签字" in text
assert "2 位审批人" in case["files"]["docs/发布流程-旧版.md"]
print(json.dumps({"expected_contains_any": ["3", "三"]}))
