# DISTILL-CANARY-2bba4069 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '73755d9e018e06957b492fa31ff8928480f5a0348ffaf9c87e3c1c18261de1ef', "fixture changed"
OPS = json.loads('[["sub", "bin/start.sh", "$(work_dir)", "$(work_dir)/run"], ["sub", "bin/stop.sh", "$(work_dir)/pid", "$(work_dir)/run/pid"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
