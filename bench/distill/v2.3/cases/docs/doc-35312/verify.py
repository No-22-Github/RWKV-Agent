# DISTILL-CANARY-4c06c701 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f53e919bbbe33e4cbe2c60969378d32dc2fbf8f9c426c94c3d5daac1fbe41d4a', "fixture changed"
OPS = json.loads('[["sub", "客服/常见问题.md", "**Q3：旧积分会过期吗？**\\nA：自 2026 年 1 月起已取消积分过期。\\n\\n**Q4：怎么联系人工客服？**", "**Q3：怎么联系人工客服？**"]]')
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
