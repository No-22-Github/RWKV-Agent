# DISTILL-CANARY-b04d8a17 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/fermentation.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

read_re = re.compile(r"^\S+ vessel=\S+ temp_c=[\d.]+ sg=\d+ reading$")
act_re = re.compile(r"^\S+ vessel=\S+ action=(\S+) amount_kg=[\d.]+$")
cent_re = re.compile(r"^\S+ vessel=\S+ action=centrifuge minutes=\d+$")
additions = 0
for line in lines[:-1]:
    m = act_re.fullmatch(line)
    if m:
        if m.group(1) == "dry-hop":
            additions += 1
    elif cent_re.fullmatch(line) or read_re.fullmatch(line):
        pass
    else:
        raise AssertionError("unreadable line: " + line)
print(json.dumps({"expected_number": additions}))
