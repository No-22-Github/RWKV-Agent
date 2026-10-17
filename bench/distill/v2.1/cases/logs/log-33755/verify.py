# DISTILL-CANARY-484c850a : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a4cd6ba167eff1ca645846a72bac8fc7ae9e7c6c5d7a6207b0f17b05ab6f5d6e', "fixture changed"
ls=files['http.log'].splitlines()
answers=[str([k for k,l in enumerate(ls,1) if ' ERROR ' in l][0])]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
