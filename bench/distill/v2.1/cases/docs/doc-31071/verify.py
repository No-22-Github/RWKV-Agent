# DISTILL-CANARY-ff1ef0d9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '782e3b58110c81299dd774ba086131ae036d9df224191af34ff0d8f0f133bf55', "fixture changed"

def apply(files, ops):
    out = dict(files)
    for op in ops:
        if op[0] == "sub":
            _, path, old, new = op
            assert out[path].count(old) == 1, (path, old)
            out[path] = out[path].replace(old, new)
        elif op[0] == "app":
            out[op[1]] = out[op[1]] + op[2]
    return out

OPS = json.loads('[["sub", "plan/checklist.md", "- [ ] 通知客服\\n", "- [x] 通知客服\\n"], ["sub", "plan/checklist.md", "- [ ] 更新状态页\\n", "- [x] 更新状态页\\n- [ ] 复盘会议\\n"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
