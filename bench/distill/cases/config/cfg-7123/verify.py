# DISTILL-CANARY-2ca2c170 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["deploy/flowerdesk.env"]

values = {}
for line in text.splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    key, sep, value = line.partition("=")
    if not sep:
        raise SystemExit("fixture guard failed: unparsable line " + repr(line))
    values[key.strip()] = value.strip()

for key in ("FLOWERDESK_REMIND_HOURS", "FLOWERDESK_MAX_BOUQUETS_PER_ORDER",
            "FLOWERDESK_DELIVERY_SLOTS", "FLOWERDESK_VASE_DEPOSIT_YUAN"):
    if key not in values:
        raise SystemExit("fixture guard failed: key " + key + " is missing")

print(json.dumps({"expected_number": int(values["FLOWERDESK_MAX_BOUQUETS_PER_ORDER"])}))
