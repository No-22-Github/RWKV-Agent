# DISTILL-CANARY-0585feea : distillation case
import json

case = json.load(open("case.json"))
poller = json.loads(case["files"]["config/poller.json"])

# README.md: a service never falls back to another block's settings.
block = poller["meter_reader"]
value = "UNKNOWN"
if "firmware_channel" in block:
    value = block["firmware_channel"]

print(json.dumps({"expected_string": value}))
