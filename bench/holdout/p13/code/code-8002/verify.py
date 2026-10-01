# DISTILL-CANARY-879aec91 : p13-holdout eval case (eval-only, never training data)
import hashlib
import json

case = json.load(open("case.json"))
files = case["files"]
cfg = json.loads(files["config/settings.json"])
if "source_dir" not in cfg or "keep_versions" not in cfg:
    raise SystemExit("settings layout changed; the snapshot is void")
snapshot = {
    path: hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    for path, content in sorted(files.items())
}
print(json.dumps({"files": snapshot}))
