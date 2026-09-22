# WORKBANK-CANARY-3f9b1c72 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
tails = [p for p in case["files"] if p.endswith(".txt")]
if len(tails) != 1:
    raise SystemExit("expected exactly one console capture, found %r" % tails)
lines = [line for line in case["files"][tails[0]].split("\n") if line.strip()]

ran = None
for line in lines:
    match = re.match(r"Ran (\d+) tests?", line.strip())
    if match:
        ran = int(match.group(1))
if ran is None:
    raise SystemExit("the capture has no 'Ran N tests' line")

passed = sum(1 for line in lines if line.endswith("... ok"))
broken = sum(
    1 for line in lines if line.endswith("... FAIL") or line.endswith("... ERROR")
)
if passed + broken != ran:
    raise SystemExit(
        "per-test evidence lists %d outcomes but the footer reports %d"
        % (passed + broken, ran)
    )

print(json.dumps({"expected": "passed" if broken == 0 else "failed"}))
