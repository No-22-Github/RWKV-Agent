# DISTILL-CANARY-4f7a1c93 : p13 holdout (eval-only)
import json

case = json.load(open("case.json", encoding="utf-8"))
staging = case["files"]["config/worker-staging.yaml"]
prod = case["files"]["config/worker-prod.yaml"]
assert "retry_limit: 3" in staging
print(json.dumps({"files": {
    "config/worker-staging.yaml": staging.replace("retry_limit: 3", "retry_limit: 5"),
    "config/worker-prod.yaml": prod,
}}))
