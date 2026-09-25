# DISTILL-CANARY-8e13b6d2 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/irrigation.log"].splitlines() if line.strip()]
opening = re.compile(r"\S+ OPEN bed=(\S+) minutes=\d+ litres=\d+")
rows = [m.group(1) for m in (opening.fullmatch(line) for line in lines) if m]
assert len(rows) == len(lines), "the journal holds a line that is not an opening"
assert len({line.split()[0][:10] for line in lines}) == 1, "the journal covers more than one day"
print(json.dumps({"expected_number": sum(1 for bed in rows if bed == "north")}))
