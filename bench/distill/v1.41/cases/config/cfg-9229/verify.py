# DISTILL-CANARY-d6cd6558 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'env/prod.env': 4, 'env/staging.env': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["env/prod.env", 2, "SMTP_PORT=465"], ["env/staging.env", 2, "SMTP_PORT=2525"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_contains_any": ["465"]}, ensure_ascii=False))
