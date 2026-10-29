# DISTILL-CANARY-a2ae387d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '07fc3ebbfc7e3fa25b1713ed2b40ba3e632d6c502d5e65d9209dbf11e70c5762', "fixture changed"
OPS = json.loads('[["sub", "ops/maintenance-windows.md", "| 2026-09-11 | search-index | Okafor |\\n", "| 2026-09-11 | search-index | Okafor |\\n| 2026-09-18 | auth-gateway | Lindqvist |\\n"]]')
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
