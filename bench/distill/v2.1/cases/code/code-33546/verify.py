# DISTILL-CANARY-a11b44a9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '93459cf8e8d63121dbd16405fb63caad9e1ce272e479a458ef1a2f9f136b899d', "fixture changed"
OPS = json.loads('[["sub", "scripts/range.py", "range(2, n) if", "range(2, n + 1) if"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
