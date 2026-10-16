# DISTILL-CANARY-b6bd56ec : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '79fa26ddd9d44dacc7075e75fc09ea9bb5ba4b80bf60bb042150b600bde8c1f8', "fixture changed"

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

OPS = json.loads('[["sub", ".env.production", "TRACE_SAMPLE_RATE=0.1\\n", "TRACE_SAMPLE_RATE=0.5\\n"], ["sub", ".env.production", "SENTRY_SAMPLE_RATE=0.1\\n", "SENTRY_SAMPLE_RATE=0.2\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
