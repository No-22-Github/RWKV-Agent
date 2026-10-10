# DISTILL-CANARY-ed01f25b : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/press-line.yaml"]

values = {}
for line in text.splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    key, sep, value = line.partition(":")
    if not sep:
        raise SystemExit("fixture guard failed: unparsable line " + repr(line))
    values[key.strip()] = value.strip()

for key in ("paper_stock_alert_pct", "print_mode", "ink_batch_check",
            "max_copies_per_job", "night_shift_queue"):
    if key not in values:
        raise SystemExit("fixture guard failed: key " + key + " is missing")

if values["print_mode"] not in ("duplex", "simplex"):
    raise SystemExit("fixture guard failed: unexpected print_mode")
if values["max_copies_per_job"] != "200":
    raise SystemExit("fixture guard failed: max_copies_per_job changed")

print(json.dumps({"expected_contains_any": ["duplex", "双面"]}))
