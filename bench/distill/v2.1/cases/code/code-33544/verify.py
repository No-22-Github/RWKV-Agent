# DISTILL-CANARY-009edf70 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9593f9200d388b1579cea12c1a77723ee26b0f595d706ab12a5dcfb1f2c1a031', "fixture changed"
OPS = json.loads('[["sub", "lib/take.js", "xs.slice(0, n - 1)", "xs.slice(0, n)"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
