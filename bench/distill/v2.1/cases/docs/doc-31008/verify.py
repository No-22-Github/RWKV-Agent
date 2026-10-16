# DISTILL-CANARY-5ac80f26 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a618108d0855cd3b1bbd71804cf31ffafc20b12263436e9c497e9939902f5639', "fixture changed"

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

OPS = json.loads('[["sub", "pricing.md", "| 团队版 | 149 | 1490 | 25 |\\n", "| 团队版 | 169 | 1690 | 25 |\\n"], ["sub", "pricing.md", "| 企业版 | 399 | 3990 | 200 |\\n", "| 企业版 | 429 | 4290 | 200 |\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
