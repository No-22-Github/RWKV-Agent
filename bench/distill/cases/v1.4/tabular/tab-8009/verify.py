# DISTILL-CANARY-ce37b9a1 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
assert "month/day/year" in case["files"]["support/README.md"]
n = 0
for r in csv.DictReader(io.StringIO(case["files"]["support/tickets-2026-08.csv"])):
    s = r["opened"]
    m = re.match(r"2026-08-(\d\d)", s) or re.match(r"08/(\d\d)/2026$", s) or re.match(r"Aug (\d+), 2026$", s)
    assert m, s
    n += r["queue"] == "billing" and int(m.group(1)) <= 14
print(json.dumps({"expected_number": n}))
