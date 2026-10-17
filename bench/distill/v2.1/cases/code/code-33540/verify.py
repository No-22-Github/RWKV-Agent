# DISTILL-CANARY-c4ab0e44 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a2a29074a1d6fe5f716960940420c6bed1829d0c56b6f55abcb73c04118c5de5', "fixture changed"
OPS = json.loads('[["sub", "bin/notify.sh", "-gt 3", "-ge 3"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
