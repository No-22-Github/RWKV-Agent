# DISTILL-CANARY-b25e7c44 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/crane-faults-2026-09.log"].splitlines()
if not lines or not lines[0].startswith("#"):
    raise SystemExit("fixture shape changed: log header line missing")
faults = []
for line in lines[1:]:
    parts = line.split()
    if len(parts) >= 3 and parts[1] == "FAULT":
        faults.append((parts[0], parts[2]))
after = [f for f in faults if f[0] >= "2026-09-15"]
out = {
    "expected_number": len(after),
    "expected_turn_2": sum(1 for d, crane in after if crane == "塔吊三号"),
}
print(json.dumps(out))
