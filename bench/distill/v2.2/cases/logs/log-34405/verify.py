# DISTILL-CANARY-7bd1b0b7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '52f2a63cbd0cda1c890bd61063210f3d48b145ed85ab907ca9a0daca25384e47', "fixture changed"
ls = [l for l in files['auth.log'].split('\n') if l]
h = [l for l in ls if 'Accepted publickey for deploy' in l]
answers = [[h[0].split()[2]], len([l for l in ls if 'Accepted publickey' in l])]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
