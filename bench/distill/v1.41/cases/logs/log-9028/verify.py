# DISTILL-CANARY-415cc455 : distillation case
import json, re
case = json.load(open("case.json"))
readme = case["files"]["审计/README.md"]
assert readme.startswith("# 审计日志")
declared = int(readme.split("共 ")[1].split(" 行")[0])
rows = case["files"]["审计/audit.log"].splitlines()
assert len(rows) == declared, (len(rows), declared)
total = 0
for row in rows:
    m = re.fullmatch(r"2026-10-\d\d \d\d:\d\d:\d\d 用户=(\S+) 动作=(\S+) 来源=gw-[a-d]", row)
    assert m, row
    total += m.group(1) == "lisi" and m.group(2) == "LOGIN_FAIL"
print(json.dumps({"expected_number": total}))
