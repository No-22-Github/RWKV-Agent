# DISTILL-CANARY-6e2d0d99 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4d5c67f6580b798ce759aa8e26f52281ceb9ee764231b196d53a1da08fc9cea2', "fixture changed"
OPS = json.loads('[["sub", "conf/lumen-scheduler.ini", "workers = 8\\n", "workers = 12\\nprefetch = 4\\n"], ["sub", "conf/lumen-scheduler.ini", "max_attempts = 3\\nbackoff = linear\\n", "max_attempts = 5\\nbackoff = exponential\\n"], ["sub", "conf/lumen-scheduler.ini", "threshold = 0.85\\n", "threshold = 0.9\\nquiet_hours = 22-06\\n"]]')
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
