# WORKBANK-CANARY-57a1ce93 : bank artifact, excluded from training corpora
import ast
import json

case = json.load(open("case.json"))

writer = None
guard = None
for path, text in sorted(case["files"].items()):
    if not path.endswith(".py"):
        continue
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name == "complete_job":
            for sub in ast.walk(node):
                if not isinstance(sub, ast.Assign):
                    continue
                target = sub.targets[0]
                if isinstance(target, ast.Attribute) and target.attr == "state":
                    writer = sub.value.value
        if node.name == "schedule_followup":
            for sub in ast.walk(node):
                if not isinstance(sub, ast.Compare):
                    continue
                left = sub.left
                if isinstance(left, ast.Attribute) and left.attr == "state":
                    guard = sub.comparators[0].value

if writer is None or guard is None:
    raise SystemExit("could not locate the state writer and the follow-up guard")
if writer == guard:
    raise SystemExit("the follow-up guard is not dead in this fixture")

print(json.dumps({"expected_contains": [writer]}))
