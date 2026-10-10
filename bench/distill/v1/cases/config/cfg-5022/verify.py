# DISTILL-CANARY-2b7e4d19 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/press-run.toml"]

# README.md: the control unit reads every run setting out of this file.
values = {}
for line in text.splitlines():
    key, _, raw = line.partition("=")
    values[key.strip()] = raw.strip()

print(json.dumps({"expected_number": int(values["blanket_wash_after_sheets"])}))
