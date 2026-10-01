# DISTILL-CANARY-2aee29ad : p13 holdout eval case (eval-only, never for training)
import json
import os
import sys

case = json.load(open("case.json"))
assets = {path: len(content) for path, content in case["files"].items() if path.endswith(".json")}
if not assets:
    sys.exit(1)
best = max(assets.items(), key=lambda kv: kv[1])
print(json.dumps({"expected_string": os.path.basename(best[0])}))
