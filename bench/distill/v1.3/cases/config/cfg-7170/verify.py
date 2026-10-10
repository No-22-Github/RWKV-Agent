# DISTILL-CANARY-47d5e3f6 : distillation case
import json

case = json.load(open("case.json"))
live = json.loads(case["files"]["config/scheduling-live.json"])
regional = json.loads(case["files"]["config/scheduling-regional.json"])
# The case premise: the same key carries conflicting values, and the deploy
# note says the deployed build predates the regional layer.
if live.get("max_advance_booking_days") != 60 or regional.get("max_advance_booking_days") != 90:
    raise SystemExit("fixture guard failed: conflicting booking windows are broken")
notes = case["files"]["docs/deploy-notes.md"]
if "rolled back to build 412" not in notes or "reads scheduling-live.json only" not in notes:
    raise SystemExit("fixture guard failed: rollback note is broken")

accepted = ["max_advance_booking_days", "advance booking", "booking window"]
print(json.dumps({"expected_contains_any": accepted}))
