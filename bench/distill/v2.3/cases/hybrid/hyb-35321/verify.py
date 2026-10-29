# DISTILL-CANARY-597f161b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '495e145028592d508afccc74bdae997f64c34683501f4a7dd63bd714da3497b0', "fixture changed"
OPS = json.loads('[["sub", "budget/offsite-2026.md", "| Catering | 1850 |\\n| **Total** | **5050** |\\n", "| Catering | 1850 |\\n| Transport | 940 |\\n| Team activity | 1275 |\\n| **Total** | **7265** |\\n"]]')
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
