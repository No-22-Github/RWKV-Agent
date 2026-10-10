# DISTILL-CANARY-b01612cc : distillation case
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

common = parse_yaml(case["files"]["config/spring-common.yaml"])
pool = parse_yaml(case["files"]["config/spring-pool.yaml"])

KEY = "max_stay_min"

if KEY not in common or KEY not in pool or common[KEY] == pool[KEY]:
    raise SystemExit("fixture guard failed: the layer conflict is broken")
if "night_patrol_gap_min" not in pool:
    raise SystemExit("fixture guard failed: pool file is broken")

# README.md: the pool area file overrides the common config.
effective = dict(common)
effective.update(pool)
print(json.dumps({"expected_number": int(effective[KEY])}))
