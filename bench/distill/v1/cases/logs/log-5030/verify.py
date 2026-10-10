# DISTILL-CANARY-41a9c358 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/aerator.log"].splitlines() if line.strip()]
close = re.fullmatch(r"\S+ CLOSE events=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(lines) - 1 == int(close.group(1)), "the journal does not list every event"

trip = re.compile(r"\S+ TRIP pond=\d+ runtime=(\d+) cause=\S+")
runtimes = [m.group(1) for m in (trip.fullmatch(line) for line in lines) if m]
assert len(runtimes) == 1, "the journal does not hold exactly one trip line"
print(json.dumps({"expected_number": int(runtimes[0])}))
