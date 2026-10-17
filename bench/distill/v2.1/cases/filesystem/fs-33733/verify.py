# DISTILL-CANARY-41621f4c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c4a07e3e3d60da49691d4772371cb06f32b88b4a6df1d8232e97ba67c6b8e90b', "fixture changed"
rows=[l.split() for l in files['inventory.txt'].splitlines()]
w=sorted(r[2] for r in rows if r[0]>='2026-09-09' and r[2].split('/')[0] in ('docs','src','test'))
answers=['docs/api.md']
assert w==['docs/api.md','docs/guide.md','src/core.go','src/main.go','src/util.go','test/core_test.go'], w
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
