# DISTILL-CANARY-68ceacf9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5a2a73c4285eeca54c14323c36eb3cfcf3fa47c4044083e5876d2f093bc08085', "fixture changed"
OPS = json.loads('[["sub", "billing/proration.py", "    ratio = days_used / days_in_cycle\\n    value = amount_cents * ratio\\n    value = round(value)\\n    if value < 0:\\n        value = 0\\n    return value\\n", "    if days_in_cycle <= 0:\\n        return 0\\n    return max(0, round(amount_cents * days_used / days_in_cycle))\\n"]]')
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
