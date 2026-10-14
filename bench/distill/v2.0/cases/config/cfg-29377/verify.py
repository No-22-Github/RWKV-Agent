# DISTILL-CANARY-531ca3e7 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'deploy/staging.env': 4, 'deploy/production.env': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["deploy/staging.env", "DB_POOL_MAX=15"], ["deploy/staging.env", "DB_POOL_MIN=2"], ["deploy/production.env", "DB_POOL_MAX=40"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["15"]}, ensure_ascii=False))
