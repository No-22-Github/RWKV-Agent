# DISTILL-CANARY-81a5c9ce : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/batch-nightly.log"].splitlines()

exit_tasks = set()
retry_tasks = set()
payout_exit = ""
payout_rerun = ""
for line in lines:
    m = re.search(r"\[([a-z-]+)\]", line)
    if not m:
        continue
    task = m.group(1)
    m2 = re.search(r"exit=(\d+)", line)
    if "] WARN" in line and m2:
        exit_tasks.add(task)
        if task == "payout":
            payout_exit = "exit=" + m2.group(1)
    if "重试" in line and "] ERROR" in line:
        retry_tasks.add(task)
    if task == "payout" and "人工补跑" in line and "开始" in line and not payout_rerun:
        payout_rerun = line.split()[1]

payout_retries = sum(1 for l in lines if "[payout]" in l and "] ERROR" in l and "重试" in l)

_cg = case["files"].get('logs/batch-nightly.log', "")
if '2026-09-26 01:08:22 [payout] ERROR 出款网关返回错误（重试 1/3）' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": payout_retries}))
