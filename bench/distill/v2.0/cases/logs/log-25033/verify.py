# DISTILL-CANARY-b93e52c0 : distillation case
import json

case = json.load(open("case.json"))
rows = [json.loads(line) for line in
        case["files"]["logs/collections.jsonl"].splitlines() if line.strip()]
day = [row for row in rows if row["round"] == "R7" and row["day"] == "2026-09-05"]
assert day, "the export holds no R7 jobs for 5 September 2026"
jobs = {row["job"]: row["bins"] for row in day}
assert len(jobs) < len(day), "the export does not show a job written out twice"
for row in day:
    assert jobs[row["job"]] == row["bins"], "a rewritten job disagrees with its first record"
print(json.dumps({"expected_number": sum(jobs.values())}))
