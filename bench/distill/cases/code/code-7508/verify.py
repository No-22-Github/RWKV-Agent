# DISTILL-CANARY-7f1b58d3 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import ast
callers = []
def_file = ""
for path in sorted(files):
    if not path.endswith(".py"):
        continue
    tree = ast.parse(files[path])
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "purge_cache":
                def_file = path.split("/")[-1]
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and (
                    (isinstance(sub.func, ast.Name) and sub.func.id == "purge_cache")
                    or (isinstance(sub.func, ast.Attribute) and sub.func.attr == "purge_cache")
                ):
                    callers.append(node.name)
facts = sorted(set(callers)) + [def_file]
print(json.dumps({"expected_contains_any": facts}))
