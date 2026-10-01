# DISTILL-CANARY-fed41943 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/build-events.jsonl"].splitlines()

failed = []
long_runs = []
long_kept = 0
repos = {}
for line in lines:
    if not line.strip():
        continue
    r = json.loads(line)
    if r["event"] == "failed":
        failed.append(r)
        repos[r["repo"]] = repos.get(r["repo"], 0) + 1
    d = r["duration_s"]
    if d is not None and d > 900:
        long_runs.append(r)
        if not (r["repo"] == "vision-core" and r["channel"] == "experimental"):
            long_kept += 1

top = sorted(repos.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
forms = ["%d builds" % len(failed), "%d failed" % len(failed), "%d failures" % len(failed),
         top,
         "%d builds" % len(long_runs), "%d runs" % len(long_runs),
         "%d builds" % long_kept, "%d runs" % long_kept]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
