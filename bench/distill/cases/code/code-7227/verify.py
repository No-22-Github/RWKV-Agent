# DISTILL-CANARY-4ec07f85 : distillation case
import ast, json

case = json.load(open("case.json"))
TARGET = "reserve_stock"
trees = {}
for path, content in case["files"].items():
    if path.endswith(".py"):
        trees[path] = ast.parse(content)
sites = sum(1 for t in trees.values() for node in ast.walk(t)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == TARGET)
print(json.dumps({"expected_number": sites}))
