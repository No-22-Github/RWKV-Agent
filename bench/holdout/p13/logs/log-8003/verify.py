# DISTILL-CANARY-005183a9 : p13-holdout eval case (eval-only, never training data)
import hashlib
import json

case = json.load(open("case.json"))
files = case["files"]
lines = [line for line in files["watchdog-export.jsonl"].splitlines() if line.strip()]
if "exported_at" not in json.loads(lines[0]):
    raise SystemExit("export meta record missing; the snapshot is void")
snapshot = {
    path: hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    for path, content in sorted(files.items())
}
print(json.dumps({"files": snapshot}))
