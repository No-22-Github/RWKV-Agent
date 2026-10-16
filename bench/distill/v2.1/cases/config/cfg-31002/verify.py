# DISTILL-CANARY-fafd3ea5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '70f32655ed8bbf54610351934fa6b00c64c840804a195fa4cdcff66bbfded841', "fixture changed"

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

OPS = json.loads('[["sub", "docker-compose.yml", "  worker:\\n    image: registry.local/shop-worker:1.4.2\\n    environment:\\n      LOG_LEVEL: info\\n", "  worker:\\n    image: registry.local/shop-worker:1.4.2\\n    environment:\\n      LOG_LEVEL: debug\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
