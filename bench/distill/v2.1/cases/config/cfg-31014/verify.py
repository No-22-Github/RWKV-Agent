# DISTILL-CANARY-12b9a110 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '536d3409632261b00baa98caa09e907f930d155c0df4eb2fff95c2541dede870', "fixture changed"

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

OPS = json.loads('[["sub", "app/limits.toml", "[tenant.pro]\\nmax_connections = 100\\n", "[tenant.pro]\\nmax_connections = 200\\n"], ["sub", "app/limits.toml", "max_connections = 200\\nidle_timeout = 60\\n", "max_connections = 200\\nidle_timeout = 90\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
