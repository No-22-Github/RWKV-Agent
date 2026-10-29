# DISTILL-CANARY-842bbd1b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f601ec6810f3d8a9f7c0c3330ffb18fbf9d3cafe607b013c09b84c2f61fed0be', "fixture changed"
OPS = json.loads('[["sub", "tools/sync_inventory.py", "    with open(path) as fh:\\n        data = json.load(fh)\\n    return {row[\'sku\']: row[\'qty\'] for row in data}\\n", "    try:\\n        with open(path) as fh:\\n            data = json.load(fh)\\n    except FileNotFoundError:\\n        return {}\\n    return {row[\'sku\']: row[\'qty\'] for row in data}\\n"]]')
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
