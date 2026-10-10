# DISTILL-CANARY-12fad306 : distillation case
import json
import re

case = json.load(open("case.json"))
loader = [line for line in case["files"]["logs/payroll-loader.log"].splitlines() if line.strip()]
failures = [line for line in loader if " ERROR " in line]
assert failures, "no failure line in the loader journal"
upstreams = {re.search(r"upstream=(\S+)", line).group(1) for line in failures}
assert len(upstreams) == 1, "the failures name more than one service"
service = upstreams.pop()
first_failure = failures[0].split()[0]

rollouts = []
for line in case["files"]["logs/fleet-release.log"].splitlines():
    row = re.fullmatch(
        r"(\S+) INFO rollout service=(\S+) build=(\d+) nodes=\d+ complete", line.strip())
    assert row is not None, "unreadable rollout line: " + line
    if row.group(2) == service and row.group(1) < first_failure:
        rollouts.append((row.group(1), int(row.group(3))))
assert rollouts, "no rollout of " + service
print(json.dumps({"expected_number": max(rollouts)[1]}))
