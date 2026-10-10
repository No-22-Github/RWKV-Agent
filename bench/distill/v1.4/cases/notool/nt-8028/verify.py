# DISTILL-CANARY-5c06e346 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "755" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork member portal")
print(json.dumps({"expected_contains_any": ["execute", "read", "write"]}))
