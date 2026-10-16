# DISTILL-CANARY-d4d39541 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '51bd3e6a5443aca3fc983ff39dea9cd15712b48d418738934087d8589dca8ac8', "fixture changed"

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

OPS = json.loads('[["app", "logs/ops-journal.log", "2026-09-16 09:50 deploy api 1.8.1 ok\\n"], ["app", "logs/ops-journal.log", "2026-09-16 10:20 rollback api 1.8.1 (latency spike)\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
