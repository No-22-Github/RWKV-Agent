# DISTILL-CANARY-068cda3b : distillation case
import json
case = json.load(open("case.json"))
LINES = {'网关日志/gw-12.log': 240, '网关日志/gw-13.log': 238, '网关日志/gw-14.log': 254, '网关日志/gw-15.log': 233, '网关日志/说明.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["网关日志/说明.md"].startswith("# 网关日志说明")
n = 0
logs = 0
for path, text in case["files"].items():
    if not path.endswith(".log"):
        continue
    logs += 1
    for row in text.splitlines():
        f = row.split(" ")
        assert len(f) == 4, row
        n += f[3] == "502"
assert logs == 4
print(json.dumps({"expected_number": n}))
