# DISTILL-CANARY-b48d062f : distillation case
import json

case = json.load(open("case.json"))
settings = json.loads(case["files"]["config/invsync.json"])

TARGET = 250  # the rollout brief ships the sync with a batch size of 250

if settings["batch_size"] == TARGET:
    raise SystemExit("fixture already carries the target batch size")

settings["batch_size"] = TARGET
print(json.dumps({"expected_stdout": str(settings["batch_size"])}))
