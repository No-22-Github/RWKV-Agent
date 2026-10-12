# DISTILL-CANARY-90f47e4c : distillation case
import json
case = json.load(open("case.json"))
LINES = {'docs/报销规则.md': 6, 'docs/报销规则-2025.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["docs/报销规则.md", "餐饮：单笔上限 150 元"], ["docs/报销规则.md", "住宿：单晚上限 600 元"], ["docs/报销规则-2025.md", "餐饮：单笔上限 100 元"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["150"]}, ensure_ascii=False))
