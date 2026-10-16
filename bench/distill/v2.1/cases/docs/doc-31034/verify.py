# DISTILL-CANARY-1ab497d3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1a352375840aec3c6c845061db66c71654fef573d5b368305b9634a794c2099b', "fixture changed"

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

OPS = json.loads('[["sub", "app/config.yaml", "api.v1.nimbus.example/v1", "api.v2.nimbus.example/v2"], ["sub", "app/client.js", "api.v1.nimbus.example/v1", "api.v2.nimbus.example/v2"], ["sub", "docs/api.md", "基础地址：https://api.v1.nimbus.example/v1", "基础地址：https://api.v2.nimbus.example/v2"], ["sub", "docs/api.md", "GET https://api.v1.nimbus.example/v1/users", "GET https://api.v2.nimbus.example/v2/users"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
