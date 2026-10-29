# DISTILL-CANARY-f14ec747 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e3fb7f6bdc7374c89281021818a91e14e7d996bd3f75dfdd583fda37f012daf4', "fixture changed"
OPS = json.loads('[["sub", "finance/vendor-spend-q3.md", "| Zephyr Cloud | 12,300 |\\n| **Total** | **24,400** |\\n", "| Delmar Print | 1,500 |\\n| Ostrand Freight | 2,600 |\\n| Zephyr Cloud | 12,300 |\\n| **Total** | **28,500** |\\n"]]')
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
