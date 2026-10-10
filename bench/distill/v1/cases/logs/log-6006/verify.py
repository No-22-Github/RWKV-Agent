# DISTILL-CANARY-b04f0ac8 : distillation case
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"]
log = case["files"]["logs/hivescale.log"]
assert readme.startswith("# Haxley Honey - hive-scale journal\n"), \
    "README.md does not document the journal"
lines = [l for l in log.splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

read_re = re.compile(r"^\S+ hive=\S+ weight_kg=[\d.]+ temp_c=[\d.]+$")
note_re = re.compile(r"^\S+ hive=\S+ NOTE .+$")
for line in lines[:-1]:
    assert read_re.fullmatch(line) or note_re.fullmatch(line), "unreadable line: " + line
# The journal only ever records scale readings and inspection notes, so it holds
# zero records of a swarm capture.
assert "swarm" not in (readme + log).lower(), "a swarm record appeared in the workspace"
print(json.dumps({"expected_contains_any": ["swarm capture", "swarm captures", "swarm"]}))
