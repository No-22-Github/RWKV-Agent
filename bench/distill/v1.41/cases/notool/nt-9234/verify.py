# DISTILL-CANARY-ae9e2fde : distillation case
import json
case = json.load(open("case.json"))
LINES = {'reports/q3-summary.txt': 1, 'reports/q4-summary.txt': 1, 'reports/tmp/draft-notes.txt': 1}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"reports/q3-summary.txt": "Third quarter revenue summary, final.\n", "reports/q4-summary.txt": "Fourth quarter revenue summary, final.\n", "reports/tmp/draft-notes.txt": "half-written outline, do not ship\n"}
print(json.dumps({"expected_contains_any": ["--exclude"]}, ensure_ascii=False))
