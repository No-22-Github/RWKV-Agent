# DISTILL-CANARY-bacf63c8 : distillation case
import ast
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"].splitlines()
head = re.match(r"^# heyuan_control —— 调用点统计范围：(\S+)", readme[0] if readme else "")
if head is None:
    raise SystemExit("fixture guard failed: README 首行缺少调用点统计范围")
scope = head.group(1)
scoped = [p for p in case["files"] if p.startswith(scope) and p.endswith(".py")]
if len(scoped) < 2:
    raise SystemExit("fixture guard failed: 统计范围内源文件不足")

count = 0
defs = 0
near_defs = 0
for path in scoped:
    tree = ast.parse(case["files"][path], path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else (
                func.attr if isinstance(func, ast.Attribute) else None)
            if name == "issue_valve_cmd":
                count += 1
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "issue_valve_cmd":
                defs += 1
            if node.name == "issue_valve_cmd_retry":
                near_defs += 1
if defs != 1:
    raise SystemExit(f"fixture guard failed: issue_valve_cmd 定义了 {defs} 次")
if near_defs < 1:
    raise SystemExit("fixture guard failed: 近名函数 issue_valve_cmd_retry 缺失")
print(json.dumps({"expected_number": count}))
