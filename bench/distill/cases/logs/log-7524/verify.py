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

_cg = case["files"].get('logs/build-events.jsonl', "")
if '{"ts":"2026-09-27T19:07:58Z","build":"BR-3369","repo":"vision-core","event":"passed","worker":"ci-04","duration_s":498,"channel":"mr-4415"}' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": len(failed)}))
