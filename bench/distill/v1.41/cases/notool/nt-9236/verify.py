# DISTILL-CANARY-64a092a1 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'notes/release-checklist.txt': 2}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"notes/release-checklist.txt": "Tag v2.0 shipped on 2026-08-30.\nNext: list what changed since the tag before writing the notes.\n"}
print(json.dumps({"expected_contains_any": ["--name-only", "--name-status"]}, ensure_ascii=False))
