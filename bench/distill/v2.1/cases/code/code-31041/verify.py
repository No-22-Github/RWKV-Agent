# DISTILL-CANARY-6ac74926 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '57a271be73ebedd52ad1072c924c5b93e1aacc06b154e81ea1e03be4392776e1', "fixture changed"

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

OPS = json.loads('[["sub", "web/index.html", "v1.9</title>", "v2.0</title>"], ["sub", "web/index.html", "Notes 1.9<", "Notes 2.0<"], ["sub", "web/about.html", "当前版本：1.9", "当前版本：2.0"], ["sub", "VERSION", "1.9.0", "2.0.0"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
