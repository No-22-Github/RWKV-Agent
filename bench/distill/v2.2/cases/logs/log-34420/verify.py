# DISTILL-CANARY-63c0cdee : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cb155632693fecfe2a99b28999546bc9e0e5c179536f141973de04144e62a2a9', "fixture changed"
import collections
c = collections.Counter(l[:10] for l in files['logs/批处理-三日合并.log'].split('\n') if ' ERROR ' in l)
d, k = c.most_common(1)[0]
answers = [[d, str(k)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
