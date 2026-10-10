# DISTILL-CANARY-ea6dc100 : distillation case
import json

case = json.load(open("case.json"))
config = json.loads(case["files"]["config/export-job.json"])
MISSING = "archive_storage_class"

# The case premise: the single config file never defines the key.
if MISSING in config:
    raise SystemExit("fixture defines " + MISSING + "; the absent-key case is broken")

# Positive control: the near-named key the decoy value comes from.
if config.get("storage_class") != "GLACIER-COLD":
    raise SystemExit("fixture guard failed: storage_class decoy is broken")

accepted = ["archive_storage_class", "archive storage class", "归档存储"]
print(json.dumps({"expected_contains_any": accepted}))
