# DISTILL-CANARY-1e70b7e3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cbc9bc22a436090f31bef303e355e2395b5d58c7beed73ae313c41bad133c17a', "fixture changed"
OPS = json.loads('[["sub", "internal/pad/pad.go", "i <= len(s)", "i < len(s)"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
