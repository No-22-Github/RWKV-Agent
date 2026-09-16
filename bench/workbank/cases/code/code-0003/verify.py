# WORKBANK-CANARY-2ea6c4d7 : bank artifact, excluded from training corpora
import ast
import json

case = json.load(open("case.json"))
callee = "release_stale_inventory_holds"
count = 0
for path in sorted(case["files"]):
    if not path.endswith(".py"):
        continue
    tree = ast.parse(case["files"][path])
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_name = isinstance(func, ast.Name) and func.id == callee
        is_attr = isinstance(func, ast.Attribute) and func.attr == callee
        if is_name or is_attr:
            count += 1
print(json.dumps({"expected_number": count}))
