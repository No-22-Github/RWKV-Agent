# DISTILL-CANARY-d239875e : distillation case
import csv
import io
import json

def build_stdout(entries):
    jobs = []
    for name in sorted(entries):
        if not name.startswith("jobs/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            added = row["added_on"]
            if "/" in added:
                d, m, y = added.split("/")
                key = f"{y}-{int(m):02d}-{int(d):02d}"
            else:
                key = added
            jobs.append((key, added, row["job_id"]))
    jobs.sort()
    lines = [f"{added},{jid}" for _, added, jid in jobs]
    lines.append(f"QUEUED,{len(jobs)}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
