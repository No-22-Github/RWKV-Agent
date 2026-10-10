# DISTILL-CANARY-afc5f6ed : distillation case
import ast
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"].splitlines()
head = re.match('^# shibei_ops —— 调用点统计范围：(\\S+)；', readme[0] if readme else "")
if head is None:
    raise SystemExit("fixture guard failed: README 首行缺少统计范围" if True else
                     "fixture guard failed: README must open with the call-site scope")
scope = head.group(1)
scoped = [p for p in case["files"] if p.startswith(scope) and p.endswith(".py")]
if len(scoped) < 2:
    raise SystemExit("fixture guard failed: scope files missing")
count = 0
defs = 0
near_defs = 0
near_calls = 0
for path in scoped:
    tree = ast.parse(case["files"][path], path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else (
                func.attr if isinstance(func, ast.Attribute) else None)
            if name == "load_model":
                count += 1
            if name == "load_model_lazy":
                near_calls += 1
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "load_model":
                defs += 1
            if node.name == "load_model_lazy":
                near_defs += 1
if defs != 1:
    raise SystemExit("fixture guard failed: load_model defined %d times" % defs)
if near_defs < 1 or near_calls < 1:
    raise SystemExit("fixture guard failed: near-name decoys missing")
print(json.dumps({"expected_number": count}))
