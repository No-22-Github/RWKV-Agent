# DISTILL-CANARY-e710e0f3 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'charts/web/values.yaml': 10, 'charts/web/values.yaml.orig': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["charts/web/values.yaml", "  limits:\n    cpu: 500m"], ["charts/web/values.yaml", "  requests:\n    cpu: 250m"], ["charts/web/values.yaml.orig", "cpu: 1000m"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["500m"]}, ensure_ascii=False))
