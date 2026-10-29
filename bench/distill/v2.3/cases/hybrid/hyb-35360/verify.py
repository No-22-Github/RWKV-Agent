# DISTILL-CANARY-40f8ccf8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7ef2513162eb83c58466ab0cff5441373d228e5a94b4ac1afa698076222d9487', "fixture changed"
OPS = json.loads('[["set", "notes/handoff-0916.txt", "Handoff for the night shift\\n- check queue lag\\n- restart the exporter if stuck\\n"], ["append", "notes/handoff-0916.txt", "- ping Okafor at 06:00\\n"]]')
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
