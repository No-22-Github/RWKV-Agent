# DISTILL-CANARY-8f02d47c : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/press-jobs-2026-09.log"].splitlines()
if not lines or not lines[0].startswith("#"):
    raise SystemExit("fixture shape changed: log header line missing")
def count(status):
    return sum(1 for line in lines[1:] if (" " + status + " ") in line)
walkerton = 0
for line in lines[1:]:
    parts = line.split()
    if len(parts) >= 6 and parts[4] == "REPRINT" and parts[5] == "Walkerton":
        walkerton += 1
out = {
    "expected_number": count("REPRINT"),
    "expected_turn_3": walkerton,
}
print(json.dumps(out))
