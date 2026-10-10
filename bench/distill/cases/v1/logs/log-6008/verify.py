# DISTILL-CANARY-b04b48e6 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/hivescale.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

feed_re = re.compile(r"^\S+ hive=(\S+) FEED syrup_kg=[\d.]+$")
read_re = re.compile(r"^\S+ hive=\S+ weight_kg=[\d.]+ temp_c=[\d.]+$")
feeds = 0
for line in lines[:-1]:
    m = feed_re.fullmatch(line)
    if m:
        if m.group(1) == "H-5":
            feeds += 1
    else:
        assert read_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": feeds}))
