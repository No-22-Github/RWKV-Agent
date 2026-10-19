# DISTILL-CANARY-65f6423d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8032c7db2cd160aec0625275733e096ba3733b7009b03d1f41797302b075e3fc', "fixture changed"
import re
ls = [l for l in files['logs/edge-proxy-0913.log'].split('\n') if l]
h = [l for l in ls if re.search(r'" 502 ', l)]
answers = [[re.search(r':(\d\d:\d\d:\d\d) ', h[0]).group(1)], len(h)]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
