# DISTILL-CANARY-76decdb2 : p13-holdout eval case (eval-only, never training data)
import json

case = json.load(open("case.json"))
entries = case["web_fixture"]
page = [e for e in entries if "release-notes" in e.get("url", "")]
if len(page) != 1 or not page[0].get("error"):
    raise SystemExit("release-notes page is reachable; the failure expectation is void")
print(json.dumps({"expected_contains_any": ["jingyun-wms.example", "release-notes", "超时", "打不开"]}))
