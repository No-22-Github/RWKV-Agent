# DISTILL-CANARY-3f83125d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '98d4999aa5fc72ae1a8d2f33e9fa5b22c102f01b2636bb41d8e104af3811936a', "fixture changed"

def apply(files, ops):
    out = dict(files)
    for op in ops:
        if op[0] == "sub":
            _, path, old, new = op
            assert out[path].count(old) == 1, (path, old)
            out[path] = out[path].replace(old, new)
        elif op[0] == "app":
            out[op[1]] = out[op[1]] + op[2]
    return out

OPS = json.loads('[["sub", "src/settings.py", "        \'NAME\': \'reports\',\\n        \'TIMEOUT\': 20,\\n", "        \'NAME\': \'reports\',\\n        \'TIMEOUT\': 120,\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
