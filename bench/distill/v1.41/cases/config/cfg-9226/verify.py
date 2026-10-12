# DISTILL-CANARY-750ca48e : distillation case
import json
case = json.load(open("case.json"))
LINES = {'部署/deploy.toml': 6, '部署/deploy.toml.orig': 6}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["部署/deploy.toml", 2, "timeout_seconds = 900"], ["部署/deploy.toml.orig", 2, "timeout_seconds = 600"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_contains_any": ["900"]}, ensure_ascii=False))
