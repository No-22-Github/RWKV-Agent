# DISTILL-CANARY-85adf81e : distillation case
import json
case = json.load(open("case.json"))
LINES = {'config/retention.yaml': 3, 'config/retention.yaml.example': 3}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
text = case["files"]["config/retention.yaml"]
assert text.splitlines()[0] == "logs_days: 30"
assert case["files"]["config/retention.yaml.example"].splitlines()[0] == "logs_days: 14"
print(json.dumps({"expected_number": int(text.splitlines()[0].split(": ")[1])}))
