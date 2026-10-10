# DISTILL-CANARY-f1982195 : distillation case
import json

case = json.load(open("case.json"))
base = json.loads(case["files"]["config/base.json"])
north = json.loads(case["files"]["config/site-north.json"])
south = json.loads(case["files"]["config/site-south.json"])

KEY = "dispatch_timeout_s"

# The site files must stay distinct and each must conflict with the base.
if not (base[KEY] != north[KEY] != south[KEY] != base[KEY]):
    raise SystemExit("fixture guard failed: layer values collapsed")
if "pod_photo_required" in north:
    raise SystemExit("fixture guard failed: base-only key leaked into the site file")

# README.md: the north site reads its own file over the base.
effective = dict(base)
effective.update(north)
if effective["pod_photo_required"] != base["pod_photo_required"]:
    raise SystemExit("fixture guard failed: fallback broken")
print(json.dumps({"expected_number": effective[KEY]}))
