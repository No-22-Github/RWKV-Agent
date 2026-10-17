# DISTILL-CANARY-80da34b0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0a3eab36fae245fe1c814af5f49a3d40b8446815907f280d23b584d6b90139ef', "fixture changed"
OPS = json.loads('[["sub", "svc/label.py", "str(to_kg(lb))", "str(round(to_kg(lb), 1))"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
