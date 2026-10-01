# DISTILL-CANARY-4b8d1f30 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/temp-alerts-2026-09.log"].splitlines()
if not lines or not lines[0].startswith("#"):
    raise SystemExit("fixture shape changed: log header line missing")
alerts = []
for line in lines[1:]:
    parts = line.split()
    if len(parts) < 3 or parts[1] != "ALERT":
        continue
    hour = int(parts[0][11:13])
    alerts.append(((hour + 8) % 24, parts[2]))
out = {
    "expected_number": len(alerts),
    "expected_turn_2": sum(1 for h, z in alerts if 9 <= h < 18),
    "expected_turn_3": sum(1 for h, z in alerts if 9 <= h < 18 and z == "冷库A区"),
}
print(json.dumps(out))
