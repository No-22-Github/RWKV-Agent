# DISTILL-CANARY-6a91c3e5 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/berth-log-2026-09.txt"].splitlines()
if not lines or not lines[0].startswith("#"):
    raise SystemExit("fixture shape changed: log header line missing")
local_day = []
for line in lines[1:]:
    parts = line.split()
    if len(parts) < 4:
        continue
    day = int(parts[0].split("-")[1])
    hour = int(parts[1].replace("Z", "").split(":")[0]) + 8
    if hour >= 24:
        day, hour = day + 1, hour - 24
    local_day.append((day, parts[3]))
eighth = [z for d, z in local_day if d == 8]
out = {
    "expected_number": len(eighth),
    "expected_turn_3": sum(1 for z in eighth if z.startswith("A")),
}
print(json.dumps(out))
