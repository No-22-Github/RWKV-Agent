# DISTILL-CANARY-deafbb22 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd433d7516570f5bd020d1e281265c0e0f41aff7dc6ce928a2b9d925ffd8d282d', "fixture changed"
out = [p for p, t in sorted(files.items()) if p.startswith('bin/') and p != 'bin/lib/common.sh' and any(l.strip().startswith('notify_slack ') or 'then notify_slack ' in l for l in t.split(chr(10)))]
assert out == ['bin/cleanup.sh', 'bin/nightly.sh'], out
ans = 'bin/nightly.sh'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
