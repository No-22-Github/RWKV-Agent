# DISTILL-CANARY-653cd085 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["logs/batch-nightly.csv"])))

abandoned = set()
digest_last_retry = ""
for row in rows:
    if row["level"] == "WARN" and ("放弃" in row["message"] or "失败" in row["message"]):
        abandoned.add(row["task"])
    if row["task"] == "digest" and row["level"] == "ERROR" and "重试" in row["message"]:
        digest_last_retry = row["ts"].split()[1]

_sabotage_guard = case["files"].get('logs/batch-nightly.csv', "")
if not _sabotage_guard.splitlines() or _sabotage_guard.splitlines()[0] != 'ts,task,level,message':
    raise SystemExit(1)
_cg = case["files"].get('logs/batch-nightly.csv', "")
if '2026-09-25 01:02:41,stock-sync,ERROR,上游目录服务无响应（重试 1/3）' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": len(abandoned)}))
