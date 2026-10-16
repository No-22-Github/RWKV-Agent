# DISTILL-CANARY-f9a38c58 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e6e171e3a4c475fa7c2ea795f842de0c366ad8911ec652eae6e7e7e6543aa798', "fixture changed"

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

OPS = json.loads('[["sub", "index.html", "  <li><a href=\\"/docs\\">文档</a></li>\\n", "  <li><a href=\\"/docs\\">文档</a></li>\\n  <li><a href=\\"/pricing\\">定价</a></li>\\n"], ["sub", "index.html", "<a href=\\"/blog\\">博客</a>", "<a href=\\"/news\\">动态</a>"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
