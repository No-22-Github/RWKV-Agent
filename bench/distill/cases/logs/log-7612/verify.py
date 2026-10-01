# DISTILL-CANARY-25829f88 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/doorlock-0912.log"].splitlines() if l.strip()]
guest = [l for l in lines if "房卡" in l]
training = [l for l in lines if "培训卡" in l]
if not guest:
    raise SystemExit(1)
rooms = {}
for l in guest:
    parts = l.split()
    room = parts[4] + " " + parts[5]
    rooms[room] = rooms.get(room, 0) + 1
top = max(sorted(rooms), key=lambda r: rooms[r])
training_card = training[0].split()[3] if training else ""
facts = [
    "%d 次" % len(guest),
    top,
    training_card,
]
print(json.dumps({"expected_contains_any": facts}))
