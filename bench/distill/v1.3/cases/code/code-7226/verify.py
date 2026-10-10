# DISTILL-CANARY-acc137cd : distillation case
import ast, json

case = json.load(open("case.json"))
TARGET = "format_waybill_no"
trees = {}
for path, content in case["files"].items():
    if path.endswith(".py"):
        trees[path] = ast.parse(content)
callers = {p for p, t in trees.items()
           for node in ast.walk(t)
           if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == TARGET}
print(json.dumps({"expected_number": len(callers)}))
