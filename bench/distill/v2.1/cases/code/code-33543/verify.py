# DISTILL-CANARY-08c334e1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8b14c7ce4237dc65fb6f872193bfd24815b7a794c5fbed182d24b24b0cd51c56', "fixture changed"
OPS = json.loads('[["sub", "search/bsearch.py", "    while lo < hi:\\n", "    while lo <= hi:\\n"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
