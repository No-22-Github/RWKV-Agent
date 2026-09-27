# DISTILL-CANARY-18398224 : distillation case
import json

case = json.load(open("case.json"))
poller = json.loads(case["files"]["config/poller.json"])

# README.md: each service reads only the block named for it.
value = poller["relay_controller"]["poll_seconds"]

print(json.dumps({"expected_number": value}))
