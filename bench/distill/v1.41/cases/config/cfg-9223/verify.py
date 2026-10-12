# DISTILL-CANARY-bd9984ae : distillation case
import json
case = json.load(open("case.json"))
LINES = {'config/prod.env': 4, 'config/prod.env.bak': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["config/prod.env", 1, "DB_HOST=db-prod-02.internal"], ["config/prod.env.bak", 1, "DB_HOST=db-prod-01.internal"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_contains_any": ["db-prod-02.internal", "db-prod-02"]}, ensure_ascii=False))
