# DISTILL-CANARY-b04f0ac8 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/hivescale.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

read_re = re.compile(r"^\S+ hive=\S+ weight_kg=[\d.]+ temp_c=[\d.]+$")
note_re = re.compile(r"^\S+ hive=\S+ NOTE .+$")
for line in lines[:-1]:
    assert read_re.fullmatch(line) or note_re.fullmatch(line), "unreadable line: " + line
# The journal only ever records scale readings and inspection notes.
print(json.dumps({"expected": "UNKNOWN"}))
