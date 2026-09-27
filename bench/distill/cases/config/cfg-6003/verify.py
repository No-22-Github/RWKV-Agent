# DISTILL-CANARY-f38aa0ea : distillation case
import configparser
import json

case = json.load(open("case.json"))
base = json.loads(case["files"]["config/orchard-base.json"])
profile = configparser.ConfigParser()
profile.read_string(case["files"]["profiles/packing-line.ini"])

# README.md: any key set in the [packing-line] profile section replaces the
# base value; keys the profile leaves out keep their base values.
KEY = "label_delay_ms"
value = base[KEY]
if profile.has_option("packing-line", KEY):
    value = int(profile.get("packing-line", KEY))

print(json.dumps({"expected_number": value}))
