# WORKBANK-CANARY-4b1e7a92 : bank artifact, excluded from training corpora
"""Expected answer for cfg-0009: the single key the live payment-settler settings
file does not declare, computed from the platform key template in case.json."""
import json
import re

case = json.load(open("case.json"))
files = case["files"]
template = files["templates/service-keys.yaml"]
config = files["config/payment-settler.yaml"]

block = re.search(r"^required_keys:\s*$\n((?:[ \t]+-\s*\S+[ \t]*\n?)+)", template, re.M)
if not block:
    raise SystemExit("required_keys block not found in templates/service-keys.yaml")
required = re.findall(r"-\s*([A-Za-z_][A-Za-z0-9_]*)", block.group(1))

configured = set(re.findall(r"^([A-Za-z_][A-Za-z0-9_]*):", config, re.M))
if len(configured) < 5:
    raise SystemExit("payment-settler settings parsed too thin: %r" % sorted(configured))

missing = [key for key in required if key not in configured]
if len(missing) != 1:
    raise SystemExit("expected exactly one missing key, got %r" % missing)

print(json.dumps({"expected_key": missing[0], "missing_count": len(missing)}))
