# DISTILL-CANARY-438259f5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bc3cff7525366c1ec29fe14418cf5a4024bab2d76708106d451fa7cc9226895c', "fixture changed"
OPS = json.loads('[["sub", "预算/客户答谢会.md", "| 场地 | 待定 |\\n| **合计** | |\\n", "| 场地 | 12000 |\\n| **合计** | **21950** |\\n"]]')
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
