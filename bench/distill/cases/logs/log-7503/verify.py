# DISTILL-CANARY-1e943192 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
batch = case["files"]["logs/batch-nightly.log"].splitlines()
ops = list(csv.DictReader(io.StringIO(case["files"]["logs/ops-actions.csv"])))

abandoned = []
seen = set()
for line in batch:
    if "] WARN" in line and ("放弃" in line or "失败" in line):
        m = re.search(r"\[([a-z-]+)\]", line)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            abandoned.append(m.group(1))

root = ""
for row in ops:
    if row["level"] == "WARN" and "凭据" in row["message"]:
        root = row["change_id"]

payout_retries = sum(1 for line in batch if "[payout]" in line and "重试" in line)

next_task = ""
next_end = ""
after_payout = False
for line in batch:
    m = re.search(r"\[([a-z-]+)\]", line)
    if not m:
        continue
    task = m.group(1)
    if task == "payout" and "WARN" in line:
        after_payout = True
        continue
    if after_payout and "INFO 开始" in line and task != "scheduler":
        next_task = task
    if next_task and task == next_task:
        next_end = line.split()[1]

_sabotage_guard = case["files"].get('logs/ops-actions.csv', "")
if not _sabotage_guard.splitlines() or _sabotage_guard.splitlines()[0] != 'time,change_id,level,message':
    raise SystemExit(1)
_cg = case["files"].get('logs/batch-nightly.log', "")
if '2026-09-27 01:03:03 [stock-sync] ERROR warehouse EAST-2 会话中断（重试 1/6）' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": payout_retries}))
