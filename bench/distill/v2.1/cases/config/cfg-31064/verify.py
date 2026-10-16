# DISTILL-CANARY-b2427e4b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '13fa3a826c4ec25ea6e5fcc882facc07f1a0c7c8dc5a09ac86df22defd8a13fe', "fixture changed"

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

OPS = json.loads('[["sub", "charts/queue.yaml", "  retry:\\n    max: 3\\n    backoff: 10\\n  consumers: 2\\n", "  retry:\\n    max: 5\\n    backoff: 10\\n    jitter: true\\n  consumers: 2\\n"], ["sub", "charts/queue.yaml", "dead_letter:\\n  enabled: true\\n", "dead_letter:\\n  enabled: false\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
