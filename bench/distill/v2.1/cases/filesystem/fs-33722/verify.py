# DISTILL-CANARY-e434c534 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '083ad4b4a490d8208eccfebfdc750d42c3614858ef34b43723f8eba38a24b633', "fixture changed"
answers=['cfg/config.prod.yaml']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
