# DISTILL-CANARY-9be59132 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f5de51306a196b965d4ee46d215106e74a2aa375d2d9a8e9952b7cc875ab4a92', "fixture changed"

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

OPS = json.loads('[["sub", "env/app.env", "APP_TIMEOUT=30", "APP_TIMEOUT=45"], ["sub", "env/app.env", "cn-east", "cn-north"], ["sub", "env/worker.env", "cn-east", "cn-north"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
