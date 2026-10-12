# DISTILL-CANARY-fba52a63 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'README.md': 10, 'README.md.bak': 10}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["README.md", 4, "- Python 3.11 or newer"], ["README.md.bak", 4, "- Python 3.8 or newer"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_contains_any": ["3.11"]}, ensure_ascii=False))
