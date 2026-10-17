# DISTILL-CANARY-9414ffbb : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3492dd929ca97e9ca9b66e9285f11814b33564140d1e84409797403995ce6c90', "fixture changed"
answers=[str(len([p for p in files if p.lower().rsplit('.',1)[-1] in ('jpg','jpeg','png','gif','webp')])), str(len([p for p in files if p.lower().rsplit('.',1)[-1] in ('mp4','mov')]))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
