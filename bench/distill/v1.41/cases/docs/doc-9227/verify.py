# DISTILL-CANARY-1dd319aa : distillation case
import json
case = json.load(open("case.json"))
LINES = {'docs/NEWS.md': 9, 'docs/NEWS-archive.md': 9}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["docs/NEWS.md", 2, "## 5.2.0 (2026-09-30)"], ["docs/NEWS-archive.md", 2, "## 4.9.3 (2025-11-18)"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_contains_any": ["5.2.0"]}, ensure_ascii=False))
