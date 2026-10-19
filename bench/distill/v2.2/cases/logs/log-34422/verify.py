# DISTILL-CANARY-edaa53b2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cf0415cfa6e4b0358ba390fd6d28541645cc69b4791893b2894ab49e89d3d117', "fixture changed"
ls = files['supervisor.log'].split('\n')
i = [k for k, l in enumerate(ls) if 'service restarted' in l][-1]
answers = [[ls[i - 1].split(': ', 1)[1].split(':')[0]]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
