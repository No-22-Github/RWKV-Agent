# DISTILL-CANARY-3c805774 : distillation case
import json
import re

case = json.load(open("case.json"))
log = case["files"]["logs/db-archive-03/backup-2026-09-15.log"]
done = [l for l in log.splitlines() if "backup-runner done" in l][0]
skipped = int(re.search(r"tables_skipped=(\d+)", done).group(1))
assert skipped == len([l for l in log.splitlines() if " skipped: " in l]) == 3
assert case["files"]["logs/db-archive-03/backup-2026-09-14.log"].startswith("2026-09-14T23:30:00Z INFO backup-runner start")
finish = done.split()[0][11:19]
print(json.dumps({"expected_contains_any": [finish, finish[:5], str(skipped), "three", "Three"]}))
