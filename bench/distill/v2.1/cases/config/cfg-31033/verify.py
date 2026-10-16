# DISTILL-CANARY-0d1bc771 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a75790afb2fe20ea0336ee1fdaaa22e6db3b57a3304018f85fff707359acb6b4', "fixture changed"

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

OPS = json.loads('[["sub", "ops/prod.env", "SERVICE_PORT=8080", "SERVICE_PORT=9090"], ["sub", "ops/prod.env", "localhost:8080", "localhost:9090"], ["sub", "ops/k8s-svc.yaml", "  - port: 8080\\n    targetPort: 8080\\n", "  - port: 9090\\n    targetPort: 9090\\n"], ["sub", "ops/readme.txt", "默认端口 8080", "默认端口 9090"], ["sub", "ops/probe.sh", "localhost:8080", "localhost:9090"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
