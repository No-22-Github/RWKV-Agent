# DISTILL-CANARY-9f273e60 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8fcf7e50000feba188b30a2072f5b7c2a5a0df0260479be82c79f495cb96a30e', "fixture changed"
OPS = json.loads('[["sub", "deploy/gate.sh", "-le \\"$FLOOR\\"", "-lt \\"$FLOOR\\""]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
