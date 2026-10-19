# DISTILL-CANARY-ec6ca4c5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a6ccd11c7e068dcdd0a643fa74bd4e88971a8585828e67ebd3e4af5bdc24bd79', "fixture changed"
import collections
c = collections.Counter(l[11:13] for l in files['logs/ledger-worker-0918.log'].split('\n') if ' ERROR ' in l)
h, k = c.most_common(1)[0]
answers = [[h + ':00', str(k)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
