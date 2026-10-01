# DISTILL-CANARY-d6ed1b8b : p13-holdout eval case (eval-only, never training data)
import hashlib
import json

case = json.load(open("case.json"))
snapshot = {
    path: hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    for path, content in sorted(case.get("files", {}).items())
}
print(json.dumps({"workspace_snapshot": snapshot}))
