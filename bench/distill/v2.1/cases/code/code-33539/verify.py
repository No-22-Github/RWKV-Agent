# DISTILL-CANARY-0a9d1ea3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '425787f84998bc934a7cfe9c67f408143696701bf6b622183070fce90b494698', "fixture changed"
OPS = json.loads('[["sub", "cmd/ring/buf.go", "if len(b.data) > b.cap {", "if len(b.data) >= b.cap {"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
