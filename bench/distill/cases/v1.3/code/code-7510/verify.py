# DISTILL-CANARY-bd58f317 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import ast
tree = ast.parse(files["net/backoff.py"])
facts = []
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "BASE_DELAY_MS":
        facts.append("BASE_DELAY_MS")
        facts.append(str(node.value.value))
    if isinstance(node, ast.ClassDef):
        facts.append(node.name)
print(json.dumps({"expected_contains_any": facts}))
