# DISTILL-CANARY-537f0222 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8bee2ae56d78cd4e0f5fc266730fdaafaae30658c7a2a8ebc05e067d5693d20f', "fixture changed"
OPS = json.loads('[["sub", "scripts/打包发布.sh", "if [ -d dist ]; then\\n  echo \\"cleaning dist\\"\\n  rm -rf dist\\n  mkdir dist\\nfi\\n\\n", "mkdir -p dist\\n\\n"], ["append", "scripts/打包发布.sh", "echo \\"done\\"\\n"]]')
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
