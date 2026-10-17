# DISTILL-CANARY-12bf5793 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8f2addcc9d922c086533bf03bc662f2a5180d0badaa81c5e019fc4655cc73df5', "fixture changed"
answers=[max(files, key=lambda p: len(files[p].encode())).split('/')[-1], max((p for p in files if '/.' not in p), key=lambda p: len(files[p].encode())).split('/')[-1]]
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
