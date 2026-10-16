# DISTILL-CANARY-1a88aea3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c45308bc0b43d07725d255aaf3edaa2b9fd2fb57c2985e034add7659cea1d3e6', "fixture changed"

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

OPS = json.loads('[["sub", "cron/jobs.txt", "sync --tz Asia/Shanghai", "sync --tz Asia/Singapore"], ["sub", "cron/jobs.txt", "weekly --tz Asia/Shanghai", "weekly --tz Asia/Singapore"], ["sub", "cron/report.conf", "Asia/Shanghai", "Asia/Singapore"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
