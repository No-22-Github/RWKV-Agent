# DISTILL-CANARY-d5b20e77 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/vat-cycle.log"].splitlines() if line.strip()]
cycle = re.compile(r"\S+ CYCLE vat=(\S+) shade=\S+ minutes=\d+ metres=\d+")
rows = [m.group(1) for m in (cycle.fullmatch(line) for line in lines) if m]
assert len(rows) == len(lines), "the journal holds a line that is not a cycle"
assert len({line.split()[0][:10] for line in lines}) == 1, "the journal covers more than one day"
print(json.dumps({"expected_number": sum(1 for vat in rows if vat == "V-3")}))
