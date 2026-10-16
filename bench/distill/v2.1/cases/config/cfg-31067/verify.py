# DISTILL-CANARY-3a77d36b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '77049b47cc0d762f1743617db30903df47b425d1b7804e5535fb51504b8a1c72', "fixture changed"

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

OPS = json.loads('[["sub", "data/menu.json", "  {\\"id\\": 3, \\"name\\": \\"粢饭\\", \\"price\\": 5}\\n", "  {\\"id\\": 3, \\"name\\": \\"粢饭\\", \\"price\\": 5},\\n  {\\"id\\": 4, \\"name\\": \\"茶叶蛋\\", \\"price\\": 2}\\n"], ["sub", "data/menu.json", "\\"name\\": \\"豆浆\\", \\"price\\": 3", "\\"name\\": \\"豆浆\\", \\"price\\": 4"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
