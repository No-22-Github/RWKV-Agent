# DISTILL-CANARY-161f83ce : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7cc0868973d4def66cc9604432fe7c8777700876012a9d317b51dee063ff81d8', "fixture changed"

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

OPS = json.loads('[["sub", "net/wg.ini", "AllowedIPs = 10.8.0.0/24\\n", "AllowedIPs = 10.8.0.0/24, 192.168.50.0/24\\n"], ["sub", "net/wg.ini", "DNS = 1.1.1.1\\n", "DNS = 10.8.0.1\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
