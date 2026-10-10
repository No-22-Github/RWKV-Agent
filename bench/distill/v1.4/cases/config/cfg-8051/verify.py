# DISTILL-CANARY-e852362c : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["README.md"].startswith("Room capacity caps")
sizes = {}
for room in ("maple", "willow", "cedar"):
    m = re.search(r"capacity: (\d+)", f["config/rooms/%s.yaml" % room])
    assert m, room
    sizes[room] = int(m.group(1))
ask = ["which two", "Which two", "which room", "Which room", "name the two rooms", "room names", "the two rooms"]
print(json.dumps({"expected_number": sizes["maple"], "expected_contains_any": ask}, ensure_ascii=False))
