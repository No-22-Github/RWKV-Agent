# DISTILL-CANARY-0ac06e45 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ce941101399ebbfa0bf4d4b4527e5db5c7c6096385da2e47855c79be238def32', "fixture changed"
OPS = json.loads('[["sub", "仓库/库存盘点.md", "| 48 |", "| 36 |"], ["sub", "仓库/库存盘点.md", "| A-104 | 移动电源 | 22 |", "| A-104 | 移动电源 | 60 |"], ["sub", "仓库/库存盘点.md", "| A-103 | 手机支架 | 75 |\\n", ""]]')
end = dict(files)
for op in OPS:
    kind, path = op[0], op[1]
    if kind == "sub":
        assert end[path].count(op[2]) == 1, (path, op[2])
        end[path] = end[path].replace(op[2], op[3])
    elif kind == "set":
        end[path] = op[2]
    else:
        t = end[path]
        end[path] = (t if t.endswith("\n") or not t else t + "\n") + op[2]
print(json.dumps({"files": {p: t for p, t in end.items() if files.get(p) != t}}, ensure_ascii=False))
