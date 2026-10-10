# DISTILL-CANARY-b8e14c70 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/compressor-2026-09.log"].splitlines()
if not lines or not lines[0].startswith("#"):
    raise SystemExit("fixture shape changed: log header line missing")
def starts(hours):
    n = 0
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 3 and parts[2] == "start" and int(parts[0][11:13]) in hours:
            n += 1
    return n
night_local = {22, 23, 0, 1, 2, 3, 4, 5}
wide = {21, 22, 23, 0, 1, 2, 3, 4, 5, 6}
out = {
    "expected_number": starts(night_local),
    "expected_turn_2": starts(wide),
}
print(json.dumps(out))
