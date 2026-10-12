# DISTILL-CANARY-5b429912 : distillation case
import json
case = json.load(open("case.json"))
text = case["files"]["config/limits.yaml"]
rows = text.splitlines()
assert rows[4] == "prod:" and rows[5] == "  upload_max_mb: 200"
assert "upload_max_mb: 10" in case["files"]["config/limits.yaml.example"]
print(json.dumps({"expected_contains_any": ["200"]}))
