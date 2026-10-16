# DISTILL-CANARY-b46d113f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '39a7feb8d7e19fdc6389b366c0da65670ecbed2fe7bfc3e88654a39e2cc8a6ad', "fixture changed"

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

OPS = json.loads('[["sub", "README.md", "```\\npip install hearth==2.3.1\\n```\\n", "```\\npip install hearth==2.4.0\\n```\\n"], ["sub", "README.md", "pip install hearth==2.3.1 --upgrade", "pip install hearth==2.4.0 --upgrade"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
