# DISTILL-CANARY-364f871b : distillation case
import json

case = json.load(open("case.json"))
lv = {}
for line in case["files"]["logs/events-2026-09-15.jsonl"].splitlines():
    e = json.loads(line)
    lv[e["level"]] = lv.get(e["level"], 0) + 1
assert sum(lv.values()) == 180
ids = sorted(int(json.loads(l)["msg"].split()[1]) for l in case["files"]["logs/events-2026-09-15.jsonl"].splitlines())
assert ids == list(range(180))
print(json.dumps({"expected_number": lv["INFO"]}))
