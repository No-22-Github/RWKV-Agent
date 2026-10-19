# DISTILL-CANARY-2b73f0e4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3f7a57a77a1487e1cc35439fa4eab705c748382a57446e3ea3ab052dee1ff300', "fixture changed"
ls = [l for l in files['gateway.log'].split('\n') if 'req-7f3a91 card auth declined' in l]
import re
m = re.search(r'code=(E-\d+) reason=(.*)$', ls[0])
answers = [[m.group(1), m.group(2)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
