# DISTILL-CANARY-e57a02c9 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/deploys-2026-09.log"].splitlines()
if not lines or not lines[0].startswith("#"):
    raise SystemExit("fixture shape changed: log header line missing")
def count(level, build, day_lo=1, day_hi=30):
    n = 0
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        day = int(parts[0][8:10])
        if day_lo <= day <= day_hi and parts[2] == level and parts[3] == "build=" + build:
            n += 1
    return n
out = {
    "expected_number": count("ERROR", "v2.4.1"),
    "expected_turn_2": count("ERROR", "v2.4.1", 7, 13),
    "expected_turn_4": count("WARN", "v2.4.1"),
}
print(json.dumps(out))
