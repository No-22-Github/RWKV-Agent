# DISTILL-CANARY-62eec327 : p13-holdout eval case (eval-only, never training data)
import hashlib
import json

case = json.load(open("case.json"))
files = case["files"]
text = files["policies/expense-policy-2026.md"]
lines = text.splitlines()
if not lines or not lines[0].startswith("# "):
    raise SystemExit("policy document layout changed; the snapshot is void")
snapshot = {
    path: hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    for path, content in sorted(files.items())
}
print(json.dumps({"files": snapshot}))
