# DISTILL-CANARY-0efe91df : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '70d5819621512013c938414f809a6296dbcde3457eb95f41a5e62c0220f07b22', "fixture changed"

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

OPS = json.loads('[["sub", "hosts.ini", "db2 ansible_host=10.0.2.12 ansible_port=22\\n", "db2 ansible_host=10.0.2.52 ansible_port=22\\n"], ["sub", "hosts.ini", "db2 ansible_host=10.0.2.52 ansible_port=22\\n", "db2 ansible_host=10.0.2.52 ansible_port=2222\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
