# DISTILL-CANARY-99c15c69 : distillation case
import json, re
case = json.load(open("case.json"))
rows = case["files"]["网关日志/gateway.log"].splitlines()
declared = int(case["files"]["网关日志/README.md"].split("共 ")[1].split(" 行")[0])
assert len(rows) == declared, (len(rows), declared)
last = None
prev = ""
for row in rows:
    m = re.fullmatch(r"\[(2026-09-\d\d \d\d:\d\d:\d\d)\] 网关 节点\d (\S+) 上游=库存服务 耗时=\d+ms", row)
    assert m, row
    if m.group(2) == "熔断打开":
        last = m.group(1)
print(json.dumps({"expected_string": last}))
