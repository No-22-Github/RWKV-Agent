# DISTILL-CANARY-80daeefc : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'db91c9b13ee3d8f3788bcc8a2669b19ca943188c6df8fcffa94b98be2a65cccd', "fixture changed"

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

OPS = json.loads('[["sub", "settings.ini", "[cache]\\nhost = cache01.internal\\nport = 6379\\ntimeout = 30\\n", "[cache]\\nhost = cache01.internal\\nport = 6379\\ntimeout = 5\\n"], ["sub", "settings.ini", "[queue]\\nhost = mq01.internal\\nport = 5672\\ntimeout = 30\\n", "[queue]\\nhost = mq01.internal\\nport = 5672\\ntimeout = 15\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
