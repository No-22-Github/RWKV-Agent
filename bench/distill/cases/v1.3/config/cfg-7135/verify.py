# DISTILL-CANARY-5a12b270 : distillation case
import json

case = json.load(open("case.json"))
base = json.loads(case["files"]["config/monitor-base.json"])
patch = json.loads(case["files"]["vendor/upgrade-patch.json"])

# Premise: the patch touches the regions array and the two lists differ, so the
# array rule actually decides the answer.
if "regions" not in base or "regions" not in patch:
    raise SystemExit("fixture guard failed: regions is missing from a layer")
if len(base["regions"]) == len(patch["regions"]):
    raise SystemExit("fixture guard failed: the array lengths no longer differ")
# Scalar rule positive control: the patch's upload interval must win.
merged = dict(base)
merged.update(patch)
if merged["upload_interval_s"] != patch["upload_interval_s"]:
    raise SystemExit("fixture guard failed: scalar override is broken")

# merge-guide.md rule three: arrays are replaced whole, not concatenated.
print(json.dumps({"expected_number": len(merged["regions"])}))
