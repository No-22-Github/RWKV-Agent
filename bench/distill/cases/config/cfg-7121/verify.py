# DISTILL-CANARY-ec79d018 : distillation case
import json

case = json.load(open("case.json"))
data = json.loads(case["files"]["config/membership.json"])

for key in ("program", "redeem_threshold", "points_per_yuan"):
    if key not in data:
        raise SystemExit("fixture guard failed: key " + key + " is missing")

print(json.dumps({"expected_number": data["redeem_threshold"]}))
