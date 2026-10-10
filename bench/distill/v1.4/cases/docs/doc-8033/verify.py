# DISTILL-CANARY-8780c216 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "after 6" in prompt and "side entrance" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork front-desk playbook")
print(json.dumps({"expected_contains_any": ["side entrance"]}))
