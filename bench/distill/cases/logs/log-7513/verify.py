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

forms = [payout_exit, "%d 次" % payout_retries]
if len(payout_rerun) >= 5:
    forms.extend([payout_rerun, payout_rerun[:5]])
forms.append("%d 个" % len(exit_tasks))
forms.append("%d 个" % len(retry_tasks))
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
