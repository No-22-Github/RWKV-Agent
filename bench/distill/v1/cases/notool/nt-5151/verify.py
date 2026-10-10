# DISTILL-CANARY-9b3c6f12 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["admin/referral-routing.txt"].splitlines():
    referral, team = [part.strip() for part in line.split("=")]
    rows[referral] = team
print(json.dumps({"expected_string": rows["continence supplies"]}))
