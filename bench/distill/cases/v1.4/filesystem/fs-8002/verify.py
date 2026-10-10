# DISTILL-CANARY-36d22f11 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["实验室/设备台账.md"]
row = [l for l in text.splitlines() if "超低温冰箱" in l][0].split("|")
room, nxt = row[3].strip(), row[5].strip()
assert nxt == "2026-10-09"
assert case["files"]["README.md"].startswith("实验平台共享资料")
print(json.dumps({"expected_string": room}))
