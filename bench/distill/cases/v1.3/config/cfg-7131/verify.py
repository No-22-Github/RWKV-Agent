# DISTILL-CANARY-cd49a1bb : distillation case
import json

case = json.load(open("case.json"))

def parse_yaml(text):
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise SystemExit("fixture guard failed: unparsable line " + repr(line))
        values[key.strip()] = value.strip()
    return values

base = parse_yaml(case["files"]["config/guestbook-base.yaml"])
building = parse_yaml(case["files"]["config/guestbook-wangshan.yaml"])
building_text = case["files"]["config/guestbook-wangshan.yaml"]

KEY = "quiet_hours_start"

if KEY not in base or KEY not in building or base[KEY] == building[KEY]:
    raise SystemExit("fixture guard failed: the layer conflict is broken")
# Positive control: the stale commented value the decoy comes from.
if "21" not in building_text:
    raise SystemExit("fixture guard failed: stale comment is gone")

# README.md: the building file overrides the base.
effective = dict(base)
effective.update(building)
print(json.dumps({"expected_number": int(effective[KEY])}))
