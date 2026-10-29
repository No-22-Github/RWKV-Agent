# DISTILL-CANARY-c26b6614 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bc2287fb5db39a60d5ea947bbae09c0166f87b34e6c2c1b311e1a830c4c46534', "fixture changed"
OPS = json.loads('[["sub", "internal/queue/worker.go", "\\tName string\\n}", "\\tName string\\n\\tRetries int\\n\\tPaused  bool\\n}"], ["sub", "internal/queue/worker.go", "\\treturn &Worker{ID: id, Name: name}", "\\treturn &Worker{ID: id, Name: name, Retries: 3}"]]')
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
