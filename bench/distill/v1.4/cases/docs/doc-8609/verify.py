# DISTILL-CANARY-fd5991c3 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "docs/billing-faq.md", "start": 4, "end": 5, "new": ["Yes. The change applies immediately.", "The price difference is prorated for the rest of the cycle."]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
