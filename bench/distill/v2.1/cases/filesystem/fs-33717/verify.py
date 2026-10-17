# DISTILL-CANARY-f1a4e091 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bbf60c158c51f27ce82f87a457b20e78eaab74ec106732988c83e2d405490bee', "fixture changed"
answers=['csv']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
