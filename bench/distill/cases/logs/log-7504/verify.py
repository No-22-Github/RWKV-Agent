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

forms = ["%d 个" % len(abandoned), digest_last_retry]
if len(digest_last_retry) >= 5:
    forms.append(digest_last_retry[:5])
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
