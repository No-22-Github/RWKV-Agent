# DISTILL-CANARY-15b5d22f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0c93242ff1ffc20c9b36cfd6244811278a609f0a1c974a67247aa3d0ee9ae491', "fixture changed"

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

OPS = json.loads('[["sub", "srv/upstream.conf", "    server 10.0.0.12:8000;\\n", "    server 10.0.0.12:8000;\\n    server 10.0.0.13:8000 backup;\\n"], ["sub", "srv/upstream.conf", "    server 10.0.0.22:3000;\\n", "    server 10.0.0.22:3000 weight=2;\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
