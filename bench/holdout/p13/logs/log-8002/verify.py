# DISTILL-CANARY-fa2edcac : p13-holdout eval case (eval-only, never training data)
import hashlib
import json

case = json.load(open("case.json"))
files = case["files"]
lines = [line for line in files["logs/checkout-20260929.jsonl"].splitlines() if line.strip()]
if json.loads(lines[0]).get("event") != "session_open":
    raise SystemExit("logstream export lost its session-open record; the snapshot is void")
snapshot = {
    path: hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    for path, content in sorted(files.items())
}
print(json.dumps({"files": snapshot}))
