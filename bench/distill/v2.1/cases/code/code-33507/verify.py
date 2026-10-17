# DISTILL-CANARY-be6f1de7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '745ed252818c56e4bab4daaeeab88c063bcd1588130a15c9fbbb4229c2708580', "fixture changed"
lines = files['deploy/prod.yaml'].split(chr(10))
idx = [i for i, l in enumerate(lines, 1) if 'timeout_seconds' in l]
ans = 'deploy/prod.yaml'
assert idx[2] == 17 and lines[idx[2]-1].strip() == 'timeout_seconds: 15'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
