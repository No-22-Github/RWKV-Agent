# DISTILL-CANARY-9d17e4c0 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/order-service-2026-04-09.log"].splitlines() if l.strip()]
close = re.search(r"日志收卷 lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) == int(close.group(1)), "line count does not match the closing record"

head_re = re.compile(r"^2026-04-09 (\d{2}:\d{2}:\d{2}) (\S+) \[(\S+)\]")
err_re = re.compile(r"^2026-04-09 (\d{2}:\d{2}:\d{2}) ERROR \[库存\] 库存扣减失败：")
deploy_done = None
for line in lines[:-1]:
    m = head_re.match(line)
    if m and m.group(3) == "部署" and "部署完成" in line:
        deploy_done = m.group(1)
assert deploy_done, "deploy record absent"
count = 0
for line in lines[:-1]:
    m = err_re.match(line)
    if m and m.group(1) > deploy_done:
        count += 1
print(json.dumps({"expected_number": count}))
