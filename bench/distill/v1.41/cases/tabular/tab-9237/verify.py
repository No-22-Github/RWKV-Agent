# DISTILL-CANARY-1e3d43a9 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'报销/2026-04.txt': 75, '报销/2026-05.txt': 83, '报销/2026-06.txt': 110, '报销/2026-07.txt': 71, '报销/2026-08.txt': 95, '报销/2026-09.txt': 75, '报销/说明.md': 4, '联系人.txt': 4, '联系人-旧.txt': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["报销/说明.md"].startswith("# 报销说明")
assert case["files"]["联系人.txt"].splitlines()[1] == "财务主管 8317"
assert case["files"]["联系人-旧.txt"].splitlines()[1] == "财务主管 8105"
n = 0
for path, text in case["files"].items():
    if path.startswith("报销/2026-") and path.endswith(".txt"):
        for r in text.splitlines():
            d, c, v = r.split(" ")
            n += int(v) * (c == "差旅")
print(json.dumps({"expected_contains_any": ["8317"] + [str(n)] + (["{:,}".format(n)] if n >= 1000 else [])}))
