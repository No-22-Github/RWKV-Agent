# DISTILL-CANARY-99756901 : p13-holdout eval case (eval-only, never training data)
import json

case = json.load(open("case.json"))
text = case["files"]["docs/care-support.md"]
lines = text.splitlines()
if not lines or not lines[0].startswith("# "):
    raise SystemExit("policy document layout changed; the clause check is void")
if "退货" in text or "退款" in text:
    raise SystemExit("return clause found; the absence expectation is void")
print(json.dumps({"expected_contains_any": ["退货", "退款"]}))
