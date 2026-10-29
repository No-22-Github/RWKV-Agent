# DISTILL-CANARY-b7f64215 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '90cf04a0f4881f82f523202228a686c8f6d1e71ac418ea8ece3cbe126a94e9d3', "fixture changed"
OPS = json.loads('[["sub", "pricing/plan-sheet-2026.md", "| Team | 15 | 119 |\\n", "| Team | 15 | 129 |\\n"], ["sub", "pricing/plan-sheet-2026.md", "| Business | 60 | 399 |\\n", "| Business | 60 | 399 |\\n| Enterprise | 250 | 1,490 |\\n"], ["append", "pricing/plan-sheet-2026.md", "Enterprise pricing includes a dedicated support contact.\\n"]]')
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
