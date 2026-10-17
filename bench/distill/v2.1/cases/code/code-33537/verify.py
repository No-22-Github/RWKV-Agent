# DISTILL-CANARY-641d2879 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ff1fa077d2c7a3ea0ebf2d9d0ed3eff9b2dbad02bf8b87980a04ddf2bdacf01b', "fixture changed"
OPS = json.loads('[["sub", "members/rules.py", "    return age > 18\\n", "    return age >= 18\\n"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
