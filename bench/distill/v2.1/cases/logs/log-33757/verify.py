# DISTILL-CANARY-65d4b67b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e4e5af09dd3cbbd437ede7ae93ddfa30057c6c461338f77acd9e472fc06ffa14', "fixture changed"
import json
rows=[json.loads(l) for l in files['events.jsonl'].splitlines()]
answers=[str([i for i,x in enumerate(rows,1) if x['level']=='error'][0])]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
