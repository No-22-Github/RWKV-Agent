# WORKBANK-CANARY-ca0f8d41 : bank artifact, excluded from training corpora
import ast
import json

case = json.load(open("case.json"))

tree = None
for path, text in sorted(case["files"].items()):
    if not path.endswith(".py"):
        continue
    candidate = ast.parse(text)
    if any(
        isinstance(node, ast.FunctionDef) and node.name == "post_entry"
        for node in candidate.body
    ):
        tree = candidate
        break
if tree is None:
    raise SystemExit("no module in the fixture defines post_entry")

imported = set()
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            imported.add(alias.name)
if not imported:
    raise SystemExit("the posting module imports no guard helper")

called = set()
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "post_entry":
        called = {
            sub.func.id
            for sub in ast.walk(node)
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
        }

missing = sorted(imported - called)
if len(missing) != 1:
    raise SystemExit(
        "expected exactly one imported guard left uncalled, got %r" % missing
    )

print(json.dumps({"expected_contains": missing}))
