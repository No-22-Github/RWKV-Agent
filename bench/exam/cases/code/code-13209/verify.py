# EXAM-CANARY-516e22a1 : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
callers = []
for path, text in sorted(case["files"].items()):
    if not path.endswith(".py") or path.startswith("pricing/"):
        continue
    if re.search(r"import apply_discount\b", text) and re.search(r"\bapply_discount\(", text):
        callers.append(path)
for want in case["turns"][1]["expect"]["output_contains"]:
    assert any(want in p for p in callers), want
assert len(callers) == len(case["turns"][1]["expect"]["output_contains"])
print(json.dumps({"expected": callers[0]}))
