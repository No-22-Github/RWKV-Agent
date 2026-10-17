# DISTILL-CANARY-abb5f371 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5893d1875cd12244a64683eff5c42e2bc252f006bdb269aacee224943cff244d', "fixture changed"
OPS = json.loads('[["sub", "app/retry.ts", "return attempt > max;", "return attempt < max;"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
