# DISTILL-CANARY-1725ef49 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'ops/oncall.md': 8, 'ops/oncall.md.bak': 8}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["ops/oncall.md", 4, "- Primary: Priya Nair"], ["ops/oncall.md.bak", 4, "- Primary: Tom Becker"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_contains_any": ["Priya"]}, ensure_ascii=False))
