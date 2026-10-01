# DISTILL-CANARY-a835c6a3 : p13-holdout eval case (eval-only, never training data)
import hashlib
import json

case = json.load(open("case.json"))
files = case["files"]
cfg = json.loads(files["settings.json"])
if "listen_port" not in cfg or "upstream_url" not in cfg:
    raise SystemExit("settings layout changed; the snapshot is void")
snapshot = {
    path: hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    for path, content in sorted(files.items())
}
print(json.dumps({"files": snapshot}))
