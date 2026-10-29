# DISTILL-CANARY-be1330ad : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ca8dda785f9b3bec16992038fe13c6b37520c703d41a8d80a22527248aa0d2d0', "fixture changed"
OPS = json.loads('[["sub", "配置/汇率服务.toml", "[legacy]\\n# 旧版接口，已于 8 月下线\\nendpoint = \\"/v1/rates\\"\\nsunset = \\"2026-08-31\\"\\nfallback = true\\n\\n", ""]]')
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
