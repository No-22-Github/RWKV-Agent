# DISTILL-CANARY-e6749b1d : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import ast
def const_value(path, name):
    tree = ast.parse(files[path])
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return node.value.value
facts = [const_value("core/loader.py", "DEFAULT_SINK"),
         const_value("core/sink.py", "DEAD_LETTER")]
tree = ast.parse(files["core/loader.py"])
for node in ast.walk(tree):
    if isinstance(node, ast.ExceptHandler) and node.type is not None:
        facts.append(node.type.id)
print(json.dumps({"expected_contains_any": facts}))
