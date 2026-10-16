# DISTILL-CANARY-d1bc731c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a7b98cc9a6cec1e14457664e141fee1c9ad3a36b0dd44dc62481d6ca9b9580ad', "fixture changed"
ans = len(set(l.split(',')[1] for l in files['regional_scores.csv'].splitlines()[4:]))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
