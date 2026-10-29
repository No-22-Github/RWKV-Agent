# DISTILL-CANARY-728fd081 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '69fe3fc7526e2ebd96b2d19116df120346f0c1c3a8d5b8f713068b575737b20f', "fixture changed"
OPS = json.loads('[["sub", "发布/更新说明.md", "# 更新说明\\n\\n", "# 更新说明\\n\\n## v3.3.0（2026-09-16）\\n- 新增离线草稿\\n- 导出支持 CSV 与 JSON\\n- 修复通知角标不清零\\n\\n"], ["sub", "发布/更新说明.md", "- 修复通知角标不清零\\n", "- 修复通知角标不清零\\n- 优化冷启动速度\\n"]]')
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
