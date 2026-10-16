# DISTILL-CANARY-f0bec6c6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cc30ef2c3cb5cc93c01368af94542997a7561f8da05638880a94a18c1db7c814', "fixture changed"

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

OPS = json.loads('[["sub", "conf/nginx.conf", "    server_name api.lantern.example;\\n    listen 8080;\\n    client_max_body_size 10m;\\n", "    server_name api.lantern.example;\\n    listen 8080;\\n    client_max_body_size 50m;\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
