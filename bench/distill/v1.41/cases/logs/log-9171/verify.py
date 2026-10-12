# DISTILL-CANARY-2bf6c0de : distillation case
import json
case = json.load(open("case.json"))
LINES = {'日志/pay-0910.log': 270, '日志/pay-0911.log': 265, '日志/pay-0912.log': 263, '日志/pay-0913.log': 236, '日志/说明.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["日志/说明.md"].startswith("# 日志说明")
n = 0
logs = 0
for path, text in case["files"].items():
    if not path.endswith(".log"):
        continue
    logs += 1
    for row in text.splitlines():
        f = row.split(" ")
        assert len(f) == 4 and f[1].startswith("level="), row
        n += f[1:] == ["level=ERROR", "svc=payment", "msg=timeout"]
assert logs == 4
print(json.dumps({"expected_number": n}))
