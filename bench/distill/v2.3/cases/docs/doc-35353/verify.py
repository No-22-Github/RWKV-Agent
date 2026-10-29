# DISTILL-CANARY-3a10e538 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4f9ce39400250459e5de66bc3b8cee55672759be4fb5fe028145b0d0da29c345', "fixture changed"
OPS = json.loads('[["append", "笔记/读书记录.md", "- 《数据密集型应用》 在读\\n"], ["append", "笔记/读书记录.md", "- 《重构》 想读\\n"]]')
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
