# DISTILL-CANARY-8ad413b9 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'值班/联系方式.md': 5, '值班/联系方式-旧.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["值班/联系方式.md", 3, "- 数据库值班：010-5550-1427"], ["值班/联系方式-旧.md", 3, "- 数据库值班：010-5550-0961"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_contains_any": ["010-5550-1427", "5550-1427"]}, ensure_ascii=False))
