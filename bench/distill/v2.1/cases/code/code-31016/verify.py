# DISTILL-CANARY-2c0b602a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0a15d7df79d85e90476ad80d53e95113a484f938efaa62299cc3d7f9b0b622e8', "fixture changed"

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

OPS = json.loads('[["sub", "src/pricing.js", "  express: 18,\\n", "  express: 22,\\n"], ["sub", "src/pricing.js", "FREE_SHIPPING_OVER = 199;", "FREE_SHIPPING_OVER = 259;"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
