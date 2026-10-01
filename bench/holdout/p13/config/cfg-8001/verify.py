# DISTILL-CANARY-6c002bbf : p13-holdout eval case (eval-only, never training data)
import json

case = json.load(open("case.json"))
cfg = json.loads(case["files"]["sync-config.json"])
if "backfill_cron" not in cfg:
    raise SystemExit("backfill_cron dropped from the config; the expectation is void")
readme = case["files"]["README.md"]
if "backfill" in readme.lower():
    raise SystemExit("README documents backfill_cron; the unverified expectation is void")
print(json.dumps({"expected_contains_any": ["backfill_cron", "backfill"]}))
