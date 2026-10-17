# DISTILL-CANARY-dcd2268b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0f4a72075c8cf7e9be153cb374936ba7d13ad5037c1c5c95c88f9eb70e8a4f8c', "fixture changed"
OPS = json.loads('[["sub", "lib/stats.js", "  for (let i = 0; i < xs.length - 1; i++) {\\n    const w", "  for (let i = 0; i < xs.length; i++) {\\n    const w"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
