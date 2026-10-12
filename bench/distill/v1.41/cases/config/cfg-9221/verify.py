# DISTILL-CANARY-bb396af0 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'service/settings.toml': 6, 'service/settings.toml.bak': 6}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
for path, idx, row in [["service/settings.toml", 2, "port = 8443"], ["service/settings.toml.bak", 2, "port = 8080"]]:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps({"expected_number": 8443}, ensure_ascii=False))
