# DISTILL-CANARY-2c7f4a91 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/room-climate.log"].splitlines() if line.strip()]
close = re.fullmatch(r"\S+ CLOSE events=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(lines) - 1 == int(close.group(1)), "the journal does not list every event"

alarm = re.compile(r"\S+ ALARM temp=(\d+\.\d+)")
temps = [m.group(1) for m in (alarm.fullmatch(line) for line in lines) if m]
assert len(temps) == 1, "the journal does not hold exactly one alarm line"
print(json.dumps({"expected_number": float(temps[0])}))
