# DISTILL-CANARY-9444cfd7 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "API" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork member portal")
print(json.dumps({"expected_contains_any": ["Application Programming Interface", "application programming interface"]}))
