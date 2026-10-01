# DISTILL-CANARY-5ebdcb87 : p13-holdout eval case (eval-only, never training data)
import hashlib
import json

case = json.load(open("case.json"))
files = case["files"]
cfg = json.loads(files["archive-policy.json"])
if "retention_days" not in cfg or "compress" not in cfg:
    raise SystemExit("config layout changed; the snapshot is void")
snapshot = {
    path: hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    for path, content in sorted(files.items())
}
print(json.dumps({"files": snapshot}))
