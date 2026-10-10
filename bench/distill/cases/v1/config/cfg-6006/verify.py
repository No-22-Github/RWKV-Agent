# DISTILL-CANARY-0585feea : distillation case
import json

case = json.load(open("case.json"))
poller = json.loads(case["files"]["config/poller.json"])

# README.md: a service never falls back to another block's settings. The case
# asserts that the meter_reader block carries no channel key; recompute that
# here. The relay_controller block does carry one, so only the meter_reader
# block is checked.
block = poller["meter_reader"]
if "firmware_channel" in block:
    raise SystemExit("meter_reader block now carries firmware_channel; the absent-object case is broken")

accepted = [
    "firmware_channel",
    "firmware channel",
    "firmware feed",
]
print(json.dumps({"expected_contains_any": accepted}))
