# DISTILL-CANARY-95a5a594 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7ff1618477bcd24c782f5ece1ec323624823f40b5a750ae4efd6b21234140f23', "fixture changed"
OPS = json.loads('[["sub", "report/dates.py", "return (b - a).days\\n", "return (b - a).days + 1\\n"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
