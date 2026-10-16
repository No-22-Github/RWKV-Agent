# DISTILL-CANARY-44c19c61 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd8fe2a875d368f96252f67b92758e545bdb93941685b8bb3fc5fab358b227d71', "fixture changed"

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

OPS = json.loads('[["app", "data/visitors.csv", "2026-09-15,1388,ads\\n2026-09-16,1502,organic\\n"], ["sub", "data/visitors.csv", "2026-09-15,1388,ads\\n", "2026-09-15,1398,ads\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
