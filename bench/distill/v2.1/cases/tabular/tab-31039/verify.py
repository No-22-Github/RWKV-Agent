# DISTILL-CANARY-86c89b67 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8d7bb30c64f8f32ea46d17c71c1a8b345dd1f2b2ba66b16efb4442e640cc05d9', "fixture changed"

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

OPS = json.loads('[["sub", "billing/rates.csv", "basic,49,0.06", "basic,49,0.08"], ["sub", "billing/rates.csv", "team,149,0.06", "team,149,0.08"], ["sub", "billing/rates.csv", "pro,399,0.06", "pro,399,0.08"], ["sub", "billing/invoice_template.txt", "税率：6%", "税率：8%"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
