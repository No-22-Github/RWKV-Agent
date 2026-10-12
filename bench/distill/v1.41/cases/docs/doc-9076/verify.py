# DISTILL-CANARY-a05a4e8f : distillation case
import json
case = json.load(open("case.json"))
text = case["files"]["README.md"]
assert text.startswith("# Orders service")
assert "listens on port 7410" in text
print(json.dumps({"expected_contains_any": ["7410"]}))
