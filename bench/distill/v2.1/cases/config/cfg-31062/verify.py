# DISTILL-CANARY-00efea33 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '86e09e8a34c78a7b157dcd928f57c000a77ec7f4cab164427ef37c879ced1707', "fixture changed"

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

OPS = json.loads('[["sub", "config/features.toml", "[\\"cn\\", \\"us\\", \\"jp\\"]", "[\\"cn\\", \\"us\\", \\"jp\\", \\"sg\\"]"], ["sub", "config/features.toml", "new_search = false", "new_search = true"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
