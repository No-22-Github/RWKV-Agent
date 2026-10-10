# DISTILL-CANARY-a05e47c8 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
data = json.loads(files["reports/pytest-summary.json"])
failed = data["failed"][0]
facts = [failed["test"], failed["error"].split(":")[0], data["suite"].split("/")[-1]]
print(json.dumps({"expected_contains_any": facts}))
