# DISTILL-CANARY-34d96667 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8c916484a6853a6a085cbbe2e3a4300c05d3ded6342b4e5e0454ab2f59864b74', "fixture changed"

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

OPS = json.loads('[["sub", "docs/limits.md", "| 旗舰 | 50 | 1000000 |\\n", "| 旗舰 | 50 | 1000000 |\\n| 定制 | 200 | 5000000 |\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
