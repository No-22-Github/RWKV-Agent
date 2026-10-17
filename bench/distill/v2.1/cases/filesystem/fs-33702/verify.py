# DISTILL-CANARY-e5035bd5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '496c3ef2ad477b3f8d025d0a28495a68f4060ad869c5247e997a81a5207be1a5', "fixture changed"
answers=[max((p for p in files if p.endswith('.csv')), key=lambda p: len(files[p].encode()))]
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
