# DISTILL-CANARY-92c6e40b : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
data = json.loads(files["out/run-summary.json"])
failed = data["failed"][0]
parts = failed["error"].split()
facts = [failed["test"], parts[1], parts[3]]
print(json.dumps({"expected_contains_any": facts}))
