# DISTILL-CANARY-72c3ec38 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'CHANGELOG.md': 12, 'CHANGELOG-v2.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["CHANGELOG.md", "Remove the --legacy flag"], ["CHANGELOG.md", "## 3.2.0\n- Deprecate the --legacy flag."], ["CHANGELOG-v2.md", "Add the --legacy flag."]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["3.4.0"]}, ensure_ascii=False))
