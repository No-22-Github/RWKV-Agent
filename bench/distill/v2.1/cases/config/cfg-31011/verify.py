# DISTILL-CANARY-37d7e44c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '04ed05ffe0ba4e89782c63741cf09f3913446728ff1b6499bc026c4659457c6c', "fixture changed"

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

OPS = json.loads('[["sub", "alerts/rules.yml", "  - alert: HighMemory\\n    expr: mem_usage > 80\\n    for: 5m\\n", "  - alert: HighMemory\\n    expr: mem_usage > 90\\n    for: 5m\\n"], ["sub", "alerts/rules.yml", "    expr: mem_usage > 90\\n    for: 5m\\n", "    expr: mem_usage > 90\\n    for: 10m\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
