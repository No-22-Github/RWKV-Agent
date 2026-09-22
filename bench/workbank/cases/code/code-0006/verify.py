# WORKBANK-CANARY-b6d24e08 : bank artifact, excluded from training corpora
import ast
import json
import re

case = json.load(open("case.json"))

suite = case["files"].get("tests/test_credit.py")
if suite is None:
    raise SystemExit("tests/test_credit.py is missing from the fixture")
tree = ast.parse(suite)
declared = [
    node.name
    for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
]

captures = [p for p in case["files"] if p.endswith(".txt")]
if len(captures) != 1:
    raise SystemExit("expected exactly one console capture, found %r" % captures)
results = re.findall(
    r"::(test_[A-Za-z0-9_]+) (PASSED|FAILED)", case["files"][captures[0]]
)
if len(results) != len(declared):
    raise SystemExit(
        "the capture lists %d results but the suite declares %d tests"
        % (len(results), len(declared))
    )

failed = sum(1 for _, outcome in results if outcome == "FAILED")
print(json.dumps({"expected_number": failed}))
