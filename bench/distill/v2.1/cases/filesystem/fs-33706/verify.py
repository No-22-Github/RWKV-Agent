# DISTILL-CANARY-33af45d7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '22091ec4075677e12cd4083c2d37c38dcc20ac75bd8a8f3683c960b1425f8a58', "fixture changed"
answers=[max(files,key=lambda p:len(files[p].encode())).split('/')[-1], max((p for p in files if '/trash/' not in p),key=lambda p:len(files[p].encode())).split('/')[-1]]
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
