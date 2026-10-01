# DISTILL-CANARY-3f6b91d2 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import ast
facts = []
tree = ast.parse(files["src/discount.py"])
for node in tree.body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
        facts.append(node.targets[0].id)
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, float):
            facts.append(str(node.value.value))
    if isinstance(node, ast.FunctionDef):
        facts.append(node.name)
print(json.dumps({"expected_contains_any": facts}))
