# DISTILL-CANARY-9c0b8779 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '69f41bd9bf14ca531ddd853623b94f4efbfa7e44d3d06399aab15dfd67020f6e', "fixture changed"
OPS = json.loads('[["set", "纪要/2026-09-16-评审.md", "# 方案评审纪要\\n\\n- 通过：缓存分层方案\\n- 待补：压测报告\\n- 下次评审：9 月 23 日\\n"]]')
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
