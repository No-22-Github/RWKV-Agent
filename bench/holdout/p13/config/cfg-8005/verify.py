# DISTILL-CANARY-9b2e6d41 : p13 holdout (eval-only)
import json

case = json.load(open("case.json", encoding="utf-8"))
conf = case["files"]["config/sync.conf"]
assert "interval_minutes = 30" in conf
print(json.dumps({"files": {
    "config/sync.conf": conf.replace("interval_minutes = 30", "interval_minutes = 15"),
}}))
