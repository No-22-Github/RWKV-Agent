# DISTILL-CANARY-d86656e6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '346851ecc0f7f21d49e5ee028fd9519b496dd6fa95d3528f3b72aa5a570c24fc', "fixture changed"
OPS = json.loads('[["sub", "采购/办公用品清单.md", "| 白板笔 | 25 | 4 | 100 |\\n| **合计** | | | **340** |\\n", "| 白板笔 | 25 | 4 | 100 |\\n| 订书机 | 12 | 15 | 180 |\\n| 文件夹 | 60 | 3 | 180 |\\n| 便利贴 | 30 | 5 | 150 |\\n| **合计** | | | **850** |\\n"]]')
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
