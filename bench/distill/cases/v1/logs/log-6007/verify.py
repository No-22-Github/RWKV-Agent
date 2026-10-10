# DISTILL-CANARY-b04a91d3 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/crate-intake.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

crate_re = re.compile(r"^\S+ station=(\S+) picker=\S+ crates=\d+ variety=\S+$")
lorry_re = re.compile(r"^\S+ lorry=\S+ loaded crates=\d+ departed$")
qa_re = re.compile(r"^\S+ QA store_temp_c=[\d.]+ pass$")
count = 0
for line in lines[:-1]:
    m = crate_re.fullmatch(line)
    if m:
        if m.group(1) == "jannerby-lane-3":
            count += 1
    else:
        assert lorry_re.fullmatch(line) or qa_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": count}))
