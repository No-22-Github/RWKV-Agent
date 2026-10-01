# DISTILL-CANARY-31d4c87b : p13-holdout eval case (eval-only, never training data)
import json

case = json.load(open("case.json"))
entries = case["web_fixture"]
incident = [e for e in entries if "incidents/payments-4021" in e.get("url", "")]
if len(incident) != 1 or not incident[0].get("error"):
    raise SystemExit("incident page is reachable; the failure expectation is void")
if not any(e.get("error") for e in entries):
    raise SystemExit("fixture lost its fetch failure; the failure expectation is void")
print(json.dumps({"expected_contains_any": ["connection reset", "status.unipalm.example", "incidents/payments-4021"]}))
