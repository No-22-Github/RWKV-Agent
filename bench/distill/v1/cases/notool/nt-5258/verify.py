# DISTILL-CANARY-829b698e : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]['safety/notify-bodies.txt'].splitlines():
    name, value = [part.strip() for part in line.split("=")]
    rows[name] = value
print(json.dumps({"expected_string": rows['bird strike']}))
