# DISTILL-CANARY-6bf3c59a : distillation case
import json

case = json.load(open("case.json"))
windows = {}
for line in case["files"]["runbook/brewhouse-shutdown.txt"].splitlines():
    vessel, window = [part.strip() for part in line.split("=")]
    windows[vessel] = window
print(json.dumps({"expected_string": windows["bright beer tank clean"]}))
