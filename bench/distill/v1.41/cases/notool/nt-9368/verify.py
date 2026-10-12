# DISTILL-CANARY-7efbcf19 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'docs/guide.md': 3, 'docs/api/ref.md': 1, 'docs/notes final.md': 1}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"docs/guide.md": "# Guide\n\nline\n", "docs/api/ref.md": "# Ref\n", "docs/notes final.md": "# Notes\n"}
print(json.dumps({"expected_contains_any": ["xargs"]}, ensure_ascii=False))
