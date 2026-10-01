# DISTILL-CANARY-6a2e8d15 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
data = json.loads(files["settings/alerts.json"])
facts = [data["route"], str(data["error_ratio_threshold"]), data["webhook"]]
print(json.dumps({"expected_contains_any": facts}))
