# DISTILL-CANARY-d2c289df : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["reports/ci-2026-09-12.txt"].splitlines()
run_re = re.compile(r"^=== CI RUN (\S+) runner=(\S+) started=(\S+) ===$")
sum_re = re.compile(r"^=== CI SUMMARY passed=(\d+) failed=(\d+) skipped=(\d+) duration=(\d+)s ===$")
runs = [i for i, line in enumerate(lines) if run_re.match(line)]
sums = [i for i, line in enumerate(lines) if sum_re.match(line)]
if len(runs) != 2 or len(sums) != 2 or not run_re.match(lines[0]):
    raise SystemExit("fixture guard failed: run/summary banners malformed")
for s in sums:
    if s < runs[-1] and s > runs[0] and s not in runs:
        pass
for a, b in zip(runs, sums):
    if b < a:
        raise SystemExit("fixture guard failed: summary precedes its run")
failed = []
claims = []
for i, line in enumerate(lines):
    m = re.match(r"^FAILED (\S+::\S+) - (.+)$", line)
    if m:
        run_idx = max(r for r in runs if r < i)
        failed.append((run_idx, m.group(1)))
    s = sum_re.match(line)
    if s:
        claims.append(int(s.group(2)))
if len(claims) != 2:
    raise SystemExit("fixture guard failed: summaries missing")
latest = runs[-1]
latest_failed = sorted(t for r, t in failed if r == latest)
earlier_failed = [t for r, t in failed if r < latest]
if claims[-1] != 0:
    raise SystemExit("fixture guard failed: 当晚汇总应声称全绿")
if len(earlier_failed) != 3 or len(latest_failed) != 1:
    raise SystemExit("fixture guard failed: 两轮 FAILED 分布异常")
value = len(latest_failed) + len(earlier_failed)
print(json.dumps({"expected_number": value}))
