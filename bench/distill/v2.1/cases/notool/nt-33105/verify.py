# DISTILL-CANARY-b0476a71 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '03abfb3b6aa8282f811d6d7b8a9c17ca2bfb9dbdd4d6b4874eb01ab271a79924', "fixture changed"
assert all(t["expect"].get("tools") == [] for t in case["turns"])
print(json.dumps({"files": case["files"]}, ensure_ascii=False))
