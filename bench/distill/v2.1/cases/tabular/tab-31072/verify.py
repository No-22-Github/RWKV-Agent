# DISTILL-CANARY-ae133484 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '668666afd8789bdeb8e09425edefc3ecdd6ed5f12463db8a013a5ab97cd87917', "fixture changed"

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

OPS = json.loads('[["sub", "data/stock.csv", "B-201,螺母 M3,0,仓2\\n", "B-201,螺母 M3,800,仓2\\n"], ["sub", "data/stock.csv", "A-101,螺丝 M4,350,仓1\\n", "A-101,螺丝 M4,350,仓3\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
