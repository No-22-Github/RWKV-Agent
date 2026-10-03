# DISTILL-CANARY-7b494842 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/card-audit-sep.log"].splitlines() if l.strip()]
# Every record is "YYYY-MM-DD HH:MM card <id> room <n> unlock OK": a malformed
# timestamp or field means the audit dump no longer parses as one.
for l in lines:
    if not re.match(r"^2026-09-08 \d\d:\d\d card [KT]-\d{4} room \d{3} unlock OK( TRAINING)?$", l):
        raise SystemExit("malformed audit line: " + l)
guest = [l for l in lines if " card K-" in l]
training = [l for l in lines if "TRAINING" in l]
if not guest:
    raise SystemExit(1)
rooms = {}
for l in guest:
    parts = l.split()
    room = parts[parts.index("room") + 1]
    rooms[room] = rooms.get(room, 0) + 1
top = max(sorted(rooms), key=lambda r: rooms[r])
training_card = training[0].split()[3] if training else ""
facts = [
    "%d guest unlocks" % len(guest),
    "room %s" % top,
    training_card,
]
print(json.dumps({"expected_contains_any": facts}))
