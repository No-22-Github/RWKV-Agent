# DISTILL-CANARY-c143c5af : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f5f7dfb7996ef05d9d00ee6e25a8524170c79abfdf8527d75ba9654acfbd1fcb', "fixture changed"

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

OPS = json.loads('[["app", "meeting/2026-09-weekly.md", "\\n## 09-16\\n- 联调完成 70%\\n- 小王负责压测\\n"], ["app", "meeting/2026-09-weekly.md", "- 下周三评审排期\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
