# DISTILL-CANARY-4e2b8d60 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/labeller.log"].splitlines() if line.strip()]
load = re.compile(r"\S+ LOAD reel=(\S+)")
jam = re.compile(r"\S+ JAM code=\S+ offset=\d+")
loads = [(index, m.group(1))
         for index, line in enumerate(lines) for m in [load.fullmatch(line)] if m]
jams = [index for index, line in enumerate(lines) if jam.fullmatch(line)]
assert loads and jams, "the journal does not hold both loads and jams"
first_jam = min(jams)
before = [reel for index, reel in loads if index < first_jam]
assert before, "the journal does not show a reel loaded ahead of the first jam"
reel = before[-1]

cores = {}
for line in case["files"]["notes/reel-intake.md"].splitlines():
    m = re.fullmatch(r"\| (\S+) \|\s*(\d+)\s*\|\s*(\d+)\s*\|.*", line)
    if m:
        cores[m.group(1)] = int(m.group(2))
assert reel in cores, "the reel loaded ahead of the first jam is not in the goods-in record"
print(json.dumps({"expected_number": cores[reel]}))
