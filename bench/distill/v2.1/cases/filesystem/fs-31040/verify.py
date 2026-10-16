# DISTILL-CANARY-127e9400 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '35ca40fdbc5f89bf9212152af7eab46381cbbfa1f8e7407cfd55eba125fdbb15', "fixture changed"

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

OPS = json.loads('[["sub", "scripts/backup.sh", "/mnt/backup/old-nas", "/mnt/backup/new-nas"], ["sub", "scripts/restore.sh", "/mnt/backup/old-nas", "/mnt/backup/new-nas"], ["sub", "docs/backup.md", "/mnt/backup/old-nas", "/mnt/backup/new-nas"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
