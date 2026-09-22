# WORKBANK-CANARY-8c3f0d16 : bank artifact, excluded from training corpora
"""Expected answer for cfg-0010: every key the catalog-sync settings file lacks.

The required key set is the union of the deployment manifest's required_keys
block and the operational keys the service README lists, so neither source on
its own yields the complete answer. Computed from case.json.
"""
import json
import re

case = json.load(open("case.json"))
files = case["files"]
manifest = files["deploy/catalog-sync.yaml"]
readme = files["services/catalog-sync/README.md"]
config = files["services/catalog-sync/settings.yaml"]

if not re.search(r"^service:\s*catalog-sync\s*$", manifest, re.M):
    raise SystemExit("catalog-sync deployment manifest header missing")

block = re.search(r"^required_keys:\s*$\n((?:[ \t]+-\s*\S+[ \t]*\n?)+)", manifest, re.M)
if not block:
    raise SystemExit("required_keys block not found in the deployment manifest")
required = re.findall(r"-\s*([A-Za-z_][A-Za-z0-9_]*)", block.group(1))

extra = re.findall(r"^- ([A-Za-z_][A-Za-z0-9_]*)\s*$", readme, re.M)
if not extra:
    raise SystemExit("no extra required keys listed in the service README")
required = required + extra

configured = set(re.findall(r"^([A-Za-z_][A-Za-z0-9_]*):", config, re.M))
missing = [key for key in required if key not in configured]
if len(missing) != 2:
    raise SystemExit("expected exactly two missing keys, got %r" % missing)

print(json.dumps({"expected_keys": missing, "missing_count": len(missing)}))
