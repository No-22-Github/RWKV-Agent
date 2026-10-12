# DISTILL-CANARY-4ca6dd6d : distillation case
import json
case = json.load(open("case.json"))
LINES = {'config/prod.env': 5, 'config/prod.env.example': 3}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["config/prod.env", "\nCACHE_TTL_SECONDS=300\n"], ["config/prod.env", "# CACHE_TTL_SECONDS=60"], ["config/prod.env.example", "CACHE_TTL_SECONDS=120"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["300"]}, ensure_ascii=False))
