# DISTILL-CANARY-a89b8541 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'CONTRIBUTING.md': 11, 'CONTRIBUTING.old.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["CONTRIBUTING.md", "bug fixes: patch/<ticket>"], ["CONTRIBUTING.md", "features: feature/<ticket>"], ["CONTRIBUTING.old.md", "bugfix/<ticket>"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["patch/"]}, ensure_ascii=False))
