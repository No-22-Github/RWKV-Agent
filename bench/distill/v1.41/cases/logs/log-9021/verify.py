# DISTILL-CANARY-ff4618e2 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["告警/说明.md"].startswith("# 告警说明")
total = 0
tsv = 0
for path, text in case["files"].items():
    if not path.endswith(".tsv"):
        continue
    tsv += 1
    rows = text.splitlines()
    assert rows[0] == "时间\t主机\t规则\t级别", path
    for row in rows[1:]:
        f = row.split("\t")
        assert len(f) == 4, row
        total += f[2] == "磁盘使用率高" and f[3] == "P1"
assert tsv == 6
print(json.dumps({"expected_number": total}))
