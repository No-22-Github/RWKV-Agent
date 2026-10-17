# DISTILL-CANARY-54ff5848 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9c2204d3a876fe9fa831035eab68b5f473e4a67f2484f81c6a616a08332d33ed', "fixture changed"
OPS = json.loads('[["sub", "src/paging.ts", "return total + 1;", "return total;"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
