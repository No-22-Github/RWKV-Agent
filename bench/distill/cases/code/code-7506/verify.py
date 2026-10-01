# DISTILL-CANARY-0d3a85f9 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import ast
facts = []
for path in sorted(files):
    if not path.endswith(".py"):
        continue
    tree = ast.parse(files[path])
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "sanitize_sku":
            facts.append(node.name)
            facts.append(path.split("/")[-1])
print(json.dumps({"expected_contains_any": facts}))
