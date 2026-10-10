# DISTILL-CANARY-206f53af : distillation case
import ast, json

case = json.load(open("case.json"))
TARGET = "recalc_cool_box"
trees = {}
for path, content in case["files"].items():
    if path.endswith(".py"):
        trees[path] = ast.parse(content)
defs = sorted({p for p, t in trees.items()
               for node in ast.walk(t)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == TARGET})
assert len(defs) == 1, "目标函数应有且只有一个定义文件: %s" % defs
print(json.dumps({"expected_contains_any": defs}, ensure_ascii=False))
