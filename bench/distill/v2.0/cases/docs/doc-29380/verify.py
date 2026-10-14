# DISTILL-CANARY-d9d15674 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'docs/退款流程.md': 5, 'docs/退款流程-旧版.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["docs/退款流程.md", "企业用户（含对公转账）：12 个工作日内处理"], ["docs/退款流程.md", "个人用户：3 个工作日"], ["docs/退款流程-旧版.md", "企业用户：20 个工作日"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["12"]}, ensure_ascii=False))
