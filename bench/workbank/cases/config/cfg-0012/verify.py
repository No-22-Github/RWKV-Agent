# WORKBANK-CANARY-a6f21c83 : bank artifact, excluded from training corpora
"""Expected answer for cfg-0012: the required set cannot be completed, because
the region profile the deployment manifest names is not in the workspace, so
whether any required key is absent cannot be determined -> UNKNOWN.

The fleet keys come from the deployment manifest and the requirement to also
cover the region profile comes from the service README; both are needed.
Computed from case.json.
"""
import json
import re

case = json.load(open("case.json"))
files = case["files"]
manifest = files["deploy/route-planner.yaml"]
readme = files["services/route-planner/README.md"]
settings = files["services/route-planner/settings.yaml"]

if not re.search(r"^service:\s*route-planner\s*$", manifest, re.M):
    raise SystemExit("route-planner deployment manifest header missing")

block = re.search(r"^required_keys:\s*$\n((?:[ \t]+-\s*\S+[ \t]*\n?)+)", manifest, re.M)
if not block:
    raise SystemExit("required_keys block not found in the deployment manifest")
required = re.findall(r"-\s*([A-Za-z_][A-Za-z0-9_]*)", block.group(1))

ref = re.search(r"^region_profile:\s*(\S+)\s*$", manifest, re.M)
if not ref:
    raise SystemExit("the manifest does not name a region profile")
profile = ref.group(1)

if "region profile" not in readme:
    raise SystemExit("the service README does not fold the region profile into the requirement")

configured = set(re.findall(r"^([A-Za-z_][A-Za-z0-9_]*):", settings, re.M))
missing = [key for key in required if key not in configured]
profile_present = profile in files

if missing or not profile_present:
    reason = ("fleet keys absent: %r" % missing) if missing else ("unresolved region profile %s" % profile)
    answer = "UNKNOWN"
else:
    answer, reason = "NONE", "every required key is declared"

print(json.dumps({"expected": answer, "reason": reason}))
