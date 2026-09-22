# WORKBANK-CANARY-e6b20c94 : bank artifact, excluded from training corpora
"""Expected answer for log-0019: number of declined authorizations in the billing log.

The count is derived from case.json by counting the records whose event field is
auth_declined, independent of the expect block and of the note text inside the file.
"""
import json

case = json.load(open("case.json"))
log = case["files"]["logs/pulsegate-billing.log"]
lines = [ln for ln in log.splitlines() if ln.strip()]

# The day's log opens with the first declined attempt; a copy missing its opening
# record is not the complete day and must not be scored as one.
if not lines or "event=auth_declined" not in lines[0]:
    raise SystemExit("pulsegate-billing log is missing its opening record")

declined = [ln for ln in lines if "event=auth_declined" in ln]
print(json.dumps({"expected_number": len(declined)}))
