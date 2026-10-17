# DISTILL-CANARY-2bc3a2b7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ff9bd9d77fb8b2a6462fbfdd4f7f3e617b278260cd99ffe6c4ee46618448079d', "fixture changed"
answers=[max(files, key=lambda p: len(files[p].encode())).split('/')[-1], sorted(files, key=lambda p: -len(files[p].encode()))[1].split('/')[-1]]
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
