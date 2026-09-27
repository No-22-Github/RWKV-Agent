# DISTILL-CANARY-f32bf446 : distillation case
import configparser
import json

case = json.load(open("case.json"))
base = json.loads(case["files"]["config/orchard-base.json"])
profile = configparser.ConfigParser()
profile.read_string(case["files"]["profiles/packing-line.ini"])

# README.md: the controller reads the base file, the profile replaces what
# it sets, and anything else is fixed in the firmware.
KEY = "pallet_wrap_tension_n"
value = "UNKNOWN"
if KEY in base:
    value = base[KEY]
elif profile.has_option("packing-line", KEY):
    value = profile.get("packing-line", KEY)

print(json.dumps({"expected_string": value}))
